import time
import threading
import logging
import platform
import subprocess

class SoundPlayer:
    """
    声音播放器
    用于播放提示音（跨平台支持）
    """
    
    @staticmethod
    def _beep(frequency: int, duration: int):
        """
        跨平台蜂鸣声
        :param frequency: 频率 (Hz)
        :param duration: 持续时间 (毫秒)
        """
        system = platform.system()
        
        if system == "Darwin":
            try:
                subprocess.run(
                    ["afplay", "/System/Library/Sounds/Ping.aiff"],
                    capture_output=True,
                    timeout=2
                )
            except Exception:
                try:
                    subprocess.run(
                        ["say", "-v", "Bells", "ding"],
                        capture_output=True,
                        timeout=2
                    )
                except Exception:
                    pass
        elif system == "Windows":
            try:
                import winsound
                winsound.Beep(frequency, duration)
            except Exception:
                pass
        else:
            try:
                print('\a', end='', flush=True)
            except Exception:
                pass

    @staticmethod
    def play_wake_up_sound():
        """
        播放唤醒提示音 (简单的上升音阶)
        """
        def _play_sequence():
            try:
                logging.info("Playing wake up sound...")
                
                system = platform.system()
                
                if system == "Darwin":
                    notes = [
                        ("/System/Library/Sounds/Ping.aiff", 0.15),
                        ("/System/Library/Sounds/Ping.aiff", 0.15),
                        ("/System/Library/Sounds/Ping.aiff", 0.15),
                        ("/System/Library/Sounds/Glass.aiff", 0.4),
                    ]
                    for sound_file, sleep_time in notes:
                        try:
                            subprocess.run(
                                ["afplay", sound_file],
                                capture_output=True,
                                timeout=2
                            )
                        except Exception:
                            pass
                        time.sleep(sleep_time)
                elif system == "Windows":
                    try:
                        import winsound
                        winsound.Beep(523, 150)
                        time.sleep(0.05)
                        winsound.Beep(659, 150)
                        time.sleep(0.05)
                        winsound.Beep(784, 150)
                        time.sleep(0.05)
                        winsound.Beep(1046, 400)
                    except Exception:
                        pass
                else:
                    for _ in range(4):
                        print('\a', end='', flush=True)
                        time.sleep(0.2)
                        
            except Exception as e:
                logging.error(f"Failed to play sound: {e}")

        threading.Thread(target=_play_sequence, daemon=True).start()

    @staticmethod
    def play_beep(frequency: int = 1000, duration: int = 200):
        """
        播放简单的蜂鸣声
        :param frequency: 频率 (Hz)
        :param duration: 持续时间 (毫秒)
        """
        def _play():
            SoundPlayer._beep(frequency, duration)
        
        threading.Thread(target=_play, daemon=True).start()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(f"Platform: {platform.system()}")
    print("Testing sound...")
    SoundPlayer.play_wake_up_sound()
    time.sleep(2)
    print("Testing beep...")
    SoundPlayer.play_beep()
    time.sleep(1)
