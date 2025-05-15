from PySide6.QtCore import QObject, Signal
from core.texture_packer import TexturePackerCore
import os
from datetime import datetime


class PackerWorker(QObject):
    finished = Signal()
    progress = Signal(object)  # (message, color) or str
    progress_percent = Signal(int)

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
        try:
            textures = TexturePackerCore.find_textures(self.folder, self.suffixes)
            total = len(textures)
            required_suffixes = list(self.suffixes.values())  # e.g., ['ambient_occlusion', 'roughness', 'metallic']

            for i, (base, maps) in enumerate(textures.items()):
                if self.stopped:
                    self._emit_progress("Operation cancelled.", "orange")
                    break

                self.progress_percent.emit(int((i + 1) / total * 100))

                missing = [key for key in required_suffixes if key not in maps]
                if missing:
                    present_keys = ', '.join(sorted(maps.keys()))
                    missing_keys = ', '.join(sorted(missing))
                    self._emit_progress(
                        f"Skipping '{base}': Missing {missing_keys}. Present: {present_keys}",
                        "red"
                    )
                    continue

                success, message = TexturePackerCore.process_texture(
                    base, maps, self.folder, self.suffixes
                )
                self._emit_progress(
                    f"✅ {message}" if success else f"Error: {message}",
                    "green" if success else "red"
                )

        except Exception as e:
            self._emit_progress(f"Critical error: {str(e)}", "red")
        finally:
            self.finished.emit()

    def _emit_progress(self, message, color=None):
        self.progress.emit((message, color) if color else message)
        if self.log_file and self.log_to_file:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"{message}\n")
