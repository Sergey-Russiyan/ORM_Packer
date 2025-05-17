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
        self.suffixes = suffixes  # Dictionary: {'ao': 'ambient_occlusion', 'roughness': 'roughness', ...}
        self.log_to_file = log_to_file
        self.stopped = False
        self.log_file = None

        if log_to_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.log_file = os.path.join(folder, f"packing_log_{timestamp}.txt")

    def run(self):
        packed_count = 0
        textures = TexturePackerCore.find_textures(self.folder, self.suffixes)
        total = len(textures)
        required_suffixes = list(self.suffixes.values())

        for i, (base, maps) in enumerate(textures.items()):
            if self.stopped:
                self._emit_progress("⚠️ Operation cancellation - completed", "orange")
                break

            self.progress_percent.emit(int((i + 1) / total * 100))

            missing = [key for key in required_suffixes if key not in maps]
            if missing:
                present_keys = ', '.join(sorted(maps.keys()))
                missing_keys = ', '.join(sorted(missing))
                self._emit_progress(
                    f"⚠️ <b>Skipping:</b> '{base}': <b>Missing:</b> {missing_keys} (texture's). <b>Present:</b> {present_keys}",
                    "orange"
                )
                continue

            success, message = TexturePackerCore.process_texture(
                base, maps, self.folder, self.suffixes
            )

            if success:
                self._emit_progress(message, "green")
                packed_count += 1
            else:
                self._emit_progress(f"⚠️ Error: {message}", "red")

        self.finished_with_count.emit(packed_count)
        self.finished.emit()

    def _emit_progress(self, message, color=None):
        if color:
            colored_message = f'<span style="color:{color}">{message}</span>'
        else:
            colored_message = message
        self.progress.emit(colored_message)
