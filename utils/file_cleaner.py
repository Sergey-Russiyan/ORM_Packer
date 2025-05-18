import os
from collections.abc import Callable


class FileCleaner:
    def __init__(self, folder_path: str, suffixes: list[str], log_callback: Callable[[str], None]):
        self.folder_path = folder_path
        self.suffixes = [s.strip().lower() for s in suffixes if s.strip()]
        self.log = log_callback

    def delete_matching_files(self):
        if not os.path.isdir(self.folder_path):
            self.log("⚠️ Invalid folder path.")
            return

        files_to_delete = self._get_matching_files()
        if not files_to_delete:
            self.log("⚠️ No files matched the given suffixes for deletion.")
            return

        return files_to_delete

    def perform_deletion(self, files: list[str]):
        deleted_count = 0
        for file in files:
            try:
                full_path = os.path.join(self.folder_path, file)
                os.remove(full_path)
                self.log(f'<span style="color:black">⚠️ <b>Deleted</b>: {file}</span>')
                deleted_count += 1
            except Exception as e:
                self.log(f"⚠️ Failed to delete {file}: {e}")
        self.log(f"❗<b>Deletion</b> complete: <b>{deleted_count}</b> files deleted.")

    def _get_matching_files(self):
        all_files = os.listdir(self.folder_path)
        self.log(f"🔍 Scanning {len(all_files)} files...")
        matched_files = []

        for f in all_files:
            full_path = os.path.join(self.folder_path, f)
            if not os.path.isfile(full_path):
                continue

            name_without_ext = os.path.splitext(f)[0].lower()

            for suffix in self.suffixes:
                if name_without_ext.endswith(suffix):
                    self.log(f"✅ Match: {f} (suffix: {suffix})")
                    matched_files.append(f)
                    break
                else:
                    self.log(f"⛔ No match: {f} (checked against: {suffix})")

        return matched_files
