import winsound
import time
import threading
import logging

class SoundPlayer:
    """
    声音播放器
    用于播放提示音
    """
    @staticmethod
    def play_wake_up_sound():
        """
        播放唤醒提示音 (简单的上升音阶)
        """
        def _play_sequence():
            try:
                logging.info("Playing wake up sound...")
                # C major chord arpeggio
                winsound.Beep(523, 150)  # C4
                time.sleep(0.05)
                winsound.Beep(659, 150)  # E4
                time.sleep(0.05)
                winsound.Beep(784, 150)  # G4
                time.sleep(0.05)
                winsound.Beep(1046, 400) # C5
            except Exception as e:
                logging.error(f"Failed to play sound: {e}")

        # 在新线程中播放，以免阻塞主逻辑
        threading.Thread(target=_play_sequence, daemon=True).start()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Testing sound...")
    SoundPlayer.play_wake_up_sound()
    time.sleep(2)
