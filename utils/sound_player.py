from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
import os


class SoundPlayer:
    def __init__(self):
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()

        self.player.setAudioOutput(self.audio_output)

        # Debugging hooks
        self.player.errorOccurred.connect(
            lambda err: print(f"[SoundPlayer] Player error: {err}")
        )
        self.player.mediaStatusChanged.connect(
            lambda status: print(f"[SoundPlayer] Media status: {status}")
        )

    def play(self, file_path: str):
        if not os.path.exists(file_path):
            print(f"[SoundPlayer] File does not exist: {file_path}")
            return

        url = QUrl.fromLocalFile(file_path)
        print(f"[SoundPlayer] Playing: {file_path}")
        self.player.setSource(url)
        self.player.play()