from core.texture_packer import TexturePackerCore
import os
from datetime import datetime
from PySide6.QtCore import QObject, Signal


class PackerWorker(QObject):
    progress = Signal(str)
    progress_percent = Signal(int)
    finished = Signal()
    finished_with_count = Signal(int)

    def __init__(self, folder, suffixes, log_to_file):
        super().__init__()

        self.folder = folder
        self.suffixes = suffixes
        self.log_to_file = log_to_file
        self.stopped = False
        self.log_fp = None

        if log_to_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.log_file_path = os.path.join(folder, f"packing_log_{timestamp}.txt")
            try:
                self.log_fp = open(self.log_file_path, "w", encoding="utf-8")
                self._log(f"== Log started at {timestamp} ==")
            except Exception as e:
                print(f"Failed to create log file: {e}")
                self.log_fp = None

    # ------------------------------------------------------------------ #
    #  Logging helpers                                                     #
    # ------------------------------------------------------------------ #

    def _log(self, message: str):
        """Write message to log file (if enabled)."""
        if self.log_fp:
            self.log_fp.write(message + "\n")
            self.log_fp.flush()

    def _emit_progress(self, message: str, color: str | None = None):
        """Emit a (optionally coloured) message to the UI."""
        if color:
            self.progress.emit(f'<span style="color:{color}">{message}</span>')
        else:
            self.progress.emit(message)

    def _log_emit(self, message: str, color: str | None = None):
        """Log + emit in one call."""
        self._log(message)
        self._emit_progress(message, color)

    # ------------------------------------------------------------------ #
    #  Diagnostics                                                         #
    # ------------------------------------------------------------------ #

    def _run_diagnostics(self) -> bool:
        """
        Verify the folder is accessible and log its raw contents.
        Returns True if everything looks fine, False if we should abort.
        """
        self._log(f"🔧 Starting packing operation in: {self.folder}")
        self._log(f"   Suffixes config: {self.suffixes}")

        # --- 1. Folder existence / accessibility ---
        if not os.path.exists(self.folder):
            msg = f"❌ Folder does not exist: {self.folder}"
            self._log_emit(msg, "red")
            return False

        if not os.path.isdir(self.folder):
            msg = f"❌ Path is not a folder: {self.folder}"
            self._log_emit(msg, "red")
            return False

        if not os.access(self.folder, os.R_OK):
            msg = f"❌ No read permission for folder: {self.folder}"
            self._log_emit(msg, "red")
            return False

        # --- 2. Raw file list ---
        try:
            all_entries = os.listdir(self.folder)
        except Exception as e:
            msg = f"❌ Cannot list folder contents: {e}"
            self._log_emit(msg, "red")
            return False

        files_only = [
            f for f in all_entries
            if os.path.isfile(os.path.join(self.folder, f))
        ]

        self._log(f"📂 Folder contains {len(all_entries)} entries "
                  f"({len(files_only)} files, "
                  f"{len(all_entries) - len(files_only)} subdirectories)")

        if not files_only:
            self._log_emit("⚠️ No files found in folder.", "orange")
            self._log("   Hint: the folder may be empty, or files may be "
                      "in subdirectories (check if find_textures uses os.walk).")
            return True  # Not fatal — let find_textures confirm

        # Log up to 40 files so the log is not huge for large projects
        preview = files_only[:40]
        self._log(f"   File preview (first {len(preview)}):")
        for f in preview:
            self._log(f"     {f}")
        if len(files_only) > 40:
            self._log(f"   ... and {len(files_only) - 40} more (truncated)")

        # --- 3. Expected-suffix presence check ---
        required_suffixes = list(self.suffixes.values())
        self._log(f"   Required suffixes: {required_suffixes}")

        matched: dict[str, list[str]] = {}   # suffix -> list of matching filenames
        for suf in required_suffixes:
            hits = [
                f for f in files_only
                if os.path.splitext(f)[0].upper().endswith(suf.upper())
            ]
            matched[suf] = hits

        any_match = any(v for v in matched.values())

        if not any_match:
            self._log("⚠️ Pre-scan: none of the required suffixes were found "
                      "in the file list (case-insensitive check).")
            self._log("   This strongly suggests a suffix mismatch.")
            self._log("   Sample filenames vs expected suffixes:")
            for suf in required_suffixes:
                self._log(f"     Looking for *{suf}.* — found 0 matches")
            # Show a few actual file stems so the user can compare
            stems = sorted({os.path.splitext(f)[0] for f in files_only[:10]})
            self._log(f"   Actual stems (first 10): {stems}")
        else:
            for suf, hits in matched.items():
                self._log(f"   Pre-scan: suffix '{suf}' → {len(hits)} file(s) found")

        return True

    # ------------------------------------------------------------------ #
    #  Main run                                                            #
    # ------------------------------------------------------------------ #

    def run(self):
        packed_count = 0

        # --- Diagnostics first ---
        if not self._run_diagnostics():
            self.finished_with_count.emit(0)
            self.finished.emit()
            if self.log_fp:
                self.log_fp.close()
            return

        # --- Discover texture groups ---
        try:
            textures = TexturePackerCore.find_textures(self.folder, self.suffixes)
        except Exception as e:
            msg = f"❌ find_textures raised an exception: {e}"
            self._log_emit(msg, "red")
            self.finished_with_count.emit(0)
            self.finished.emit()
            if self.log_fp:
                self.log_fp.close()
            return

        total = len(textures)
        required_suffixes = list(self.suffixes.values())

        self._log(f"Found {total} texture group(s) to process.")
        self._log(f"Required suffixes: {required_suffixes}")

        if total == 0:
            # Extra hint logged after find_textures returns empty
            self._log(
                "⚠️ find_textures returned 0 groups. Possible causes:\n"
                "   1. Suffix case mismatch (e.g. files use '_ao' but config says '_AO').\n"
                "   2. Unsupported file extension (e.g. .tga, .tif not in the allowed list).\n"
                "   3. find_textures only scans the top-level folder but files are in subfolders.\n"
                "   4. Grouping logic requires ALL suffixes present; if any one is missing the "
                "group is silently dropped.\n"
                "   Check TexturePackerCore.find_textures for the exact filtering logic."
            )
            self._emit_progress(
                "⚠️ No texture groups found. See the log file for a diagnostic report.",
                "orange"
            )
            self.finished_with_count.emit(0)
            self.finished.emit()
            if self.log_fp:
                self.log_fp.close()
            return

        # --- Process each group ---
        for i, (base, maps) in enumerate(textures.items()):
            if self.stopped:
                self._log_emit("⚠️ Operation cancelled by user.", "orange")
                break

            self.progress_percent.emit(int((i + 1) / total * 100))

            missing = [key for key in required_suffixes if key not in maps]
            if missing:
                present_keys = ', '.join(sorted(maps.keys()))
                missing_keys = ', '.join(sorted(missing))
                msg = (
                    f"⚠️ Skipping '{base}': missing {missing_keys}. "
                    f"Present: {present_keys}"
                )
                self._log_emit(msg, "orange")
                continue

            try:
                success, message = TexturePackerCore.process_texture(
                    base, maps, self.folder, self.suffixes
                )
            except Exception as e:
                msg = f"❌ Exception while processing '{base}': {e}"
                self._log_emit(msg, "red")
                continue

            if success:
                self._log_emit(f"✅ {message}", "green")
                packed_count += 1
            else:
                self._log_emit(f"⚠️ Error: {message}", "red")

        self._log(f"🏁 Finished. Packed {packed_count}/{total} successfully.")
        self.finished_with_count.emit(packed_count)
        self.finished.emit()
        if self.log_fp:
            self.log_fp.close()
