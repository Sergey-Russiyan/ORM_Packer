from core.texture_packer import TexturePackerCore
import os
from datetime import datetime
from PySide6.QtCore import QObject, Signal


class PackerWorker(QObject):
    progress = Signal(str)  # or Signal(object) if you send tuples
    progress_percent = Signal(int)
    finished = Signal()
    finished_with_count = Signal(int)

    def __init__(self, folder, suffixes, log_to_file):
        super().__init__()

        self.folder = folder
        self.suffixes = suffixes
        self.log_to_file = log_to_file
        self.stopped = False
        self.log_file = None
        self.log_fp = None  # ✅ Always define this, regardless of log_to_file

        if log_to_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.log_file_path = os.path.join(folder, f"packing_log_{timestamp}.txt")
            try:
                self.log_fp = open(self.log_file_path, "w", encoding="utf-8")
                self._log(f"== Log started at {timestamp} ==")
            except Exception as e:
                print(f"Failed to create log file: {e}")
                self.log_fp = None

    def _log(self, message: str):
        """Write message to file and emit progress signal"""
        if self.log_fp:
            self.log_fp.write(message + "\n")
            self.log_fp.flush()

    def run(self):
        packed_count = 0
        textures = TexturePackerCore.find_textures(self.folder, self.suffixes)
        total = len(textures)
        required_suffixes = list(self.suffixes.values())

        self._log(f"🔧 Starting packing operation in: {self.folder}")
        self._log(f"Found {total} texture groups to process.")
        self._log(f"Required suffixes: {required_suffixes}")

        for i, (base, maps) in enumerate(textures.items()):
            if self.stopped:
                self._emit_progress("⚠️ Operation cancellation - completed", "orange")
                self._log("⚠️ Operation cancelled by user.")
                break

            self.progress_percent.emit(int((i + 1) / total * 100))

            missing = [key for key in required_suffixes if key not in maps]
            if missing:
                present_keys = ', '.join(sorted(maps.keys()))
                missing_keys = ', '.join(sorted(missing))
                msg = (
                    f"⚠️ Skipping: '{base}': Missing: {missing_keys} (textures). "
                    f"Present: {present_keys}"
                )
                self._emit_progress(msg, "orange")
                self._log(msg)
                continue

            success, message = TexturePackerCore.process_texture(
                base, maps, self.folder, self.suffixes
            )

            if success:
                self._emit_progress(message, "green")
                self._log(f"✅ {message}")
                packed_count += 1
            else:
                self._emit_progress(f"⚠️ Error: {message}", "red")
                self._log_line(f"❌ Error: {message}")

        self._log(f"🏁 Finished. Packed {packed_count}/{total} successfully.")
        self.finished_with_count.emit(packed_count)
        self.finished.emit()
        if self.log_fp:
            self.log_fp.close()

    def _emit_progress(self, message, color=None):
        if color:
            colored_message = f'<span style="color:{color}">{message}</span>'
        else:
            colored_message = message
        self.progress.emit(colored_message)
