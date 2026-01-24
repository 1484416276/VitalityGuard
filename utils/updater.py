import os
import sys
import json
import logging
import threading
import time
import urllib.request
import urllib.error
import shutil
from version import __version__

# GitHub Repo Info
REPO_OWNER = "1484416276"
REPO_NAME = "VitalityGuard"
GITHUB_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"

def _compare_versions(v1, v2):
    """
    Compare two version strings (e.g., "1.0.8" vs "1.0.9").
    Returns:
        1 if v1 > v2
        0 if v1 == v2
        -1 if v1 < v2
    """
    def parse(v):
        return [int(x) for x in v.strip("v").split(".")]
    
    try:
        p1 = parse(v1)
        p2 = parse(v2)
        return (p1 > p2) - (p1 < p2)
    except Exception:
        return 0

class Updater:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.logger = logging.getLogger("VitalityGuard.Updater")

    def start_check_loop(self):
        """Start the update check loop in a daemon thread."""
        thread = threading.Thread(target=self._check_loop, daemon=True)
        thread.start()

    def _check_loop(self):
        """Check for updates periodically (e.g., every 4 hours)."""
        while True:
            try:
                config = self.config_manager.reload_config() # Reload to get latest setting
                if config.get("auto_update", True):
                    self._check_and_update()
            except Exception as e:
                self.logger.error(f"Error in update loop: {e}")
            
            # Sleep for 4 hours (4 * 60 * 60)
            time.sleep(14400)

    def _check_and_update(self):
        self.logger.info(f"Checking for updates... Current version: {__version__}")
        try:
            # 1. Fetch release info
            # Use a timeout to avoid hanging
            with urllib.request.urlopen(GITHUB_API_URL, timeout=10) as response:
                if response.status != 200:
                    self.logger.warning(f"Failed to fetch release info: HTTP {response.status}")
                    return
                data = json.loads(response.read().decode())
            
            tag_name = data.get("tag_name", "")
            if not tag_name:
                return

            # 2. Compare versions
            if _compare_versions(tag_name, __version__) <= 0:
                self.logger.info("No new version found.")
                return
            
            self.logger.info(f"New version found: {tag_name}")

            # 3. Find asset
            assets = data.get("assets", [])
            download_url = None
            asset_name = ""
            for asset in assets:
                name = asset.get("name", "")
                if name.endswith(".exe") and "VitalityGuard" in name:
                    download_url = asset.get("browser_download_url")
                    asset_name = name
                    break
            
            if not download_url:
                self.logger.warning("No suitable EXE asset found in release.")
                return

            # 4. Download
            self._perform_download_and_swap(download_url, asset_name, tag_name)

        except urllib.error.URLError as e:
            self.logger.warning(f"Network error checking updates: {e}")
        except Exception as e:
            self.logger.exception(f"Unexpected error checking updates: {e}")

    def _perform_download_and_swap(self, url, filename, version):
        """
        Download the new EXE and prepare it for the next launch.
        Strategy:
        1. Download to `VitalityGuard_new.exe`.
        2. Rename current `VitalityGuard.exe` to `VitalityGuard.exe.old`.
        3. Rename `VitalityGuard_new.exe` to `VitalityGuard.exe`.
        4. Do NOT restart. Windows allows renaming the running executable, 
           but not deleting it. The next time the user starts the app, 
           it will run the new one.
        """
        if not getattr(sys, "frozen", False):
            self.logger.info("Running in script mode. Skipping update download.")
            return

        current_exe = sys.executable
        exe_dir = os.path.dirname(current_exe)
        temp_exe = os.path.join(exe_dir, f"update_{version}.tmp")
        
        try:
            self.logger.info(f"Downloading update from {url}...")
            # Download
            with urllib.request.urlopen(url, timeout=300) as response, open(temp_exe, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
            
            self.logger.info("Download complete.")

            # Prepare for swap
            # We need to rename the RUNNING exe. Windows allows this!
            # But we can't overwrite it directly.
            
            # Cleanup old backups if any
            old_backup = current_exe + ".old"
            if os.path.exists(old_backup):
                try:
                    os.remove(old_backup)
                except OSError:
                    self.logger.info("Could not remove previous backup (likely locked/running?), skipping.")
            
            # Rename current -> old
            try:
                os.rename(current_exe, old_backup)
            except OSError as e:
                self.logger.error(f"Failed to rename current exe: {e}")
                # Clean temp
                os.remove(temp_exe)
                return

            # Rename new -> current
            try:
                os.rename(temp_exe, current_exe)
                self.logger.info(f"Update applied successfully! {version} will run on next startup.")
            except OSError as e:
                self.logger.error(f"Failed to move new exe to place: {e}")
                # Try to rollback
                try:
                    os.rename(old_backup, current_exe)
                except:
                    self.logger.critical("FATAL: Failed to rollback exe!")
                os.remove(temp_exe)

        except Exception as e:
            self.logger.exception(f"Update failed during download/swap: {e}")
            if os.path.exists(temp_exe):
                try:
                    os.remove(temp_exe)
                except:
                    pass
