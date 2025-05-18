import json
import os
import webbrowser
from pathlib import Path
from typing import Optional, Dict, Any, cast, Union, Tuple

from PySide6.QtCore import QThread, QTimer, QPoint, Signal, QObject
from PySide6.QtWidgets import (QApplication, QMessageBox, QPushButton, QToolTip,
                               QSizePolicy, QWidget, QVBoxLayout, QHBoxLayout,
                               QLineEdit, QLabel, QTextEdit, QProgressBar,
                               QGroupBox, QCheckBox, QFileDialog)
from pkg_resources import ResourceManager

from utils.file_cleaner import FileCleaner
from utils.path_utils import get_base_dir, resource_path
from settings.settings_manager import SettingsManager
from worker.packer_worker import PackerWorker
from utils.sound_player import SoundPlayer


class Signals(QObject):
    """Centralized signal handling for worker communication"""
    progress = Signal(str)
    progress_with_color = Signal(str, str)
    progress_percent = Signal(int)
    finished = Signal()
    finished_with_count = Signal(int)


class TexturePackerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_initial_state()
        self._init_ui()
        self._load_settings()
        self._setup_connections()
        self._setup_signal_connections()

    def _setup_initial_state(self):
        """Initialize all state variables"""
        self.settings = SettingsManager()
        self.resource_manager = self._init_resource_manager()
        self.sound_player = SoundPlayer()
        self.worker_thread: Optional[QThread] = None
        self.worker: Optional[PackerWorker] = None
        self.cleaner: Optional[FileCleaner] = None
        self.packed_files_count = 0
        self.signals = Signals()

    @staticmethod
    def _init_resource_manager() -> 'ResourceManager':
        """Initialize the resource manager with tooltips"""
        base_dir = Path(__file__).parent
        path = base_dir / '..' / 'resources' / 'i18n' / 'tooltips_en.json'
        return ResourceManager(str(path.resolve()))

    def _init_ui(self):
        """Initialize all UI components"""
        self.setWindowTitle("ORM Texture Packer. By Serhii Ru.")
        self.resize(720, 540)
        self.setAcceptDrops(True)

        # Create all UI elements
        self._create_folder_ui()
        self._create_suffix_ui()
        self._create_log_ui()
        self._create_advanced_ui()
        buttons_container = self._create_buttons()

        # Main layout
        layout = QVBoxLayout(self)
        layout.addLayout(self.folder_layout)
        layout.addLayout(self.suffix_layout)
        layout.addWidget(self.log_output)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.advanced_button)
        layout.addWidget(self.advanced_options_group)
        layout.addWidget(buttons_container)

    def _create_folder_ui(self):
        self.folder_layout = QHBoxLayout()
        self.folder_path_edit = QLineEdit()
        self.folder_button = self.make_button("📁", "exp_button_t")
        self.folder_clear_button = self.make_button("❌", "clear_button_t")

        self.folder_layout.addWidget(QLabel("Path to Folder:"))
        self.folder_layout.addWidget(self.folder_path_edit)
        self.folder_layout.addWidget(self.folder_button)
        self.folder_layout.addWidget(self.folder_clear_button)

    def _create_suffix_ui(self):
        self.suffix_layout = QVBoxLayout()

        # Create suffix input fields
        self.ao_suffix = QLineEdit()
        self.roughness_suffix = QLineEdit()
        self.metallic_suffix = QLineEdit()

        # Add suffix rows
        for label_text, field in [
            ("'AO' suffix:", self.ao_suffix),
            ("'Roughness' suffix:", self.roughness_suffix),
            ("'Metallic' suffix:", self.metallic_suffix)
        ]:
            row = QHBoxLayout()
            label = QLabel(label_text)
            label.setFixedWidth(120)
            row.addWidget(label)
            row.addWidget(field)
            self.suffix_layout.addLayout(row)

    def _create_log_ui(self):
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

    def _create_advanced_ui(self):
        # Advanced options toggle button
        self.advanced_button = self.make_button("Advanced Options ▼", "adv_opt_button_t")
        self.advanced_button.setCheckable(True)

        # Advanced options group
        self.advanced_options_group = QGroupBox("Advanced Options")
        self.advanced_options_group.setVisible(False)

        # Checkboxes
        self.export_log_checkbox = QCheckBox("📝 Export log to file")
        self.dark_theme_checkbox = QCheckBox("🌙 Dark theme")
        self.sound_checkbox = QCheckBox("🔔 Play sound on finish")

        # Layout
        advanced_layout = QHBoxLayout()
        advanced_layout.addWidget(self.export_log_checkbox)
        advanced_layout.addWidget(self.dark_theme_checkbox)
        advanced_layout.addWidget(self.sound_checkbox)
        self.advanced_options_group.setLayout(advanced_layout)

    def _create_buttons(self):
        # Main buttons container
        buttons_container = QWidget()
        buttons_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        main_layout = QHBoxLayout(buttons_container)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 1. Start Button Section (1/3 width)
        start_container = QWidget()
        start_layout = QHBoxLayout(start_container)
        start_layout.setContentsMargins(0, 0, 0, 0)

        self.pack_button = self.make_button("🔄 Start Pack", "pack_button_t")
        self.pack_button.setObjectName("packButton")
        self.delete_button = self.make_button("🗑️ Delete Files", "delete_button_t")
        self.delete_button.setObjectName("deleteButton")

        self.pack_button.setFixedHeight(60)
        start_layout.addWidget(self.pack_button)
        main_layout.addWidget(start_container, stretch=1)

        self.delete_button.setFixedHeight(60)
        start_layout.addWidget(self.delete_button)

        # 2. Right Buttons Section (2/3 width total)
        right_container = QWidget()
        right_layout = QHBoxLayout(right_container)
        right_layout.setSpacing(10)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # First column (1/3 width)
        col1 = QWidget()
        col1_layout = QVBoxLayout(col1)
        col1_layout.setSpacing(5)
        self.cancel_button = self.make_button("✋ Cancel", "cancel_button_t")
        self.manual_button = self.make_button("📖 Manual", "manual_button_t")
        for btn in [self.cancel_button, self.manual_button]:
            btn.setFixedHeight(30)
        col1_layout.addWidget(self.cancel_button)
        col1_layout.addWidget(self.manual_button)
        right_layout.addWidget(col1, stretch=1)

        # Second column (1/3 width)
        col2 = QWidget()
        col2_layout = QVBoxLayout(col2)
        col2_layout.setSpacing(5)
        self.buy_button = self.make_button("☕ Buy me a Coffee", "coffee_button_t")
        self.feedback_button = self.make_button("📧 Write Email", "email_button_t")
        for btn in [self.buy_button, self.feedback_button]:
            btn.setFixedHeight(30)
        col2_layout.addWidget(self.buy_button)
        col2_layout.addWidget(self.feedback_button)
        right_layout.addWidget(col2, stretch=1)

        main_layout.addWidget(right_container, stretch=2)
        return buttons_container

    def _setup_connections(self):
        """Setup all signal-slot connections"""
        # Folder operations
        self.folder_button.clicked.connect(self._select_folder)
        self.folder_clear_button.clicked.connect(lambda: self.folder_path_edit.setText(""))

        # Main operations
        self.pack_button.clicked.connect(self._start_packing)
        self.delete_button.clicked.connect(self._handle_delete_files)

        # Button actions
        self.cancel_button.clicked.connect(self._cancel_packing)
        self.manual_button.clicked.connect(self._show_manual)
        self.buy_button.clicked.connect(self._open_donation_link)
        self.feedback_button.clicked.connect(self._open_email_client)
        self.advanced_button.clicked.connect(self._toggle_advanced_options)

        # Checkbox actions
        self.dark_theme_checkbox.stateChanged.connect(self._on_theme_checkbox_changed)
        self.export_log_checkbox.stateChanged.connect(self._on_checkbox_changed)
        self.sound_checkbox.stateChanged.connect(self._on_checkbox_changed)

    def _setup_signal_connections(self):
        """Connect all worker signals to their handlers"""
        self.signals.progress.connect(self._handle_log_output)
        self.signals.progress_with_color.connect(
            lambda text, color: self._handle_log_output(f'<span style="color:{color}">{text}</span>')
        )
        self.signals.progress_percent.connect(self.progress_bar.setValue)
        self.signals.finished.connect(self._finish_packing)
        self.signals.finished_with_count.connect(self._handle_finished_count)

    def make_button(self, text: str, tooltip_key: Optional[str] = None) -> 'DelayedTooltipButton':
        """Factory method for creating consistent buttons with tooltips"""
        return DelayedTooltipButton(
            text,
            tooltip_key,
            resource_manager=self.resource_manager
        )

    def _handle_delete_files(self):
        """Handle file deletion with confirmation"""
        folder_path = self.folder_path_edit.text().strip()
        suffixes = [
            self.ao_suffix.text(),
            self.roughness_suffix.text(),
            self.metallic_suffix.text(),
        ]

        self.cleaner = FileCleaner(folder_path, suffixes, self.log_output.append)
        files_to_delete = self.cleaner.delete_matching_files()

        if not files_to_delete:
            return

        # Show confirmation dialog
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Confirm Delete")
        msg_box.setText(f"Are you sure you want to delete {len(files_to_delete)} files?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
        msg_box.setDefaultButton(QMessageBox.StandardButton.Cancel)
        result = msg_box.exec()

        if result == QMessageBox.StandardButton.Yes:
            self.cleaner.perform_deletion(files_to_delete)
        else:
            self.log_output.append("⚠️ Delete operation canceled.")

    def _toggle_advanced_options(self):
        """Toggle visibility of advanced options"""
        visible = self.advanced_button.isChecked()
        self.advanced_options_group.setVisible(visible)
        self.advanced_button.setText(
            "Advanced Options ▲" if visible else "Advanced Options ▼"
        )

    def _on_theme_checkbox_changed(self, state: int):
        """Handle theme change checkbox"""
        dark_theme = bool(state)
        self._apply_theme(dark_theme)
        self._save_settings()

    def _on_checkbox_changed(self, state):
        """Generic checkbox change handler"""
        self._save_settings()

    @staticmethod
    def _apply_theme(dark_theme: bool):
        """Apply the selected theme to the application"""
        try:
            base_dir = get_base_dir()
            theme_file = "dark_theme.qss" if dark_theme else "light_theme.qss"
            theme_path = os.path.join(base_dir, "resources", theme_file)

            if os.path.exists(theme_path):
                with open(theme_path, "r", encoding='utf-8') as f:
                    stylesheet = f.read()

                if dark_theme:
                    stylesheet += "\n QWidget { background-color: #222; color: #eee; }"
                else:
                    stylesheet += "\n QWidget { background-color: #fff; color: #000; }"

                app = QApplication.instance()
                if app is not None:
                    app = cast(QApplication, app)
                    app.setStyle("Fusion")
                    app.setStyleSheet("")
                    QApplication.processEvents()
                    app.setStyleSheet(stylesheet)

                # Refresh all widgets
                for widget in app.allWidgets():
                    widget.style().unpolish(widget)
                    widget.style().polish(widget)
                    widget.update()

        except Exception as e:
            print(f"Error applying theme: {str(e)}")

    def _load_settings(self):
        """Load settings from persistent storage"""
        settings = self.settings.load_settings()

        # Dark theme checkbox + theme application
        dark_theme = bool(settings['advanced']['dark_theme'])
        self.dark_theme_checkbox.setChecked(dark_theme)
        self._apply_theme(dark_theme)

        # Other UI elements
        self.folder_path_edit.setText(settings['folder'])
        self.ao_suffix.setText(settings['suffixes']['ao'])
        self.roughness_suffix.setText(settings['suffixes']['roughness'])
        self.metallic_suffix.setText(settings['suffixes']['metallic'])
        self.export_log_checkbox.setChecked(settings['advanced']['export_log'])
        self.sound_checkbox.setChecked(settings['advanced']['play_sound'])

    def _save_settings(self):
        """Save current settings to persistent storage"""
        current_settings = {
            'folder': self.folder_path_edit.text(),
            'suffixes': {
                'ao': self.ao_suffix.text(),
                'roughness': self.roughness_suffix.text(),
                'metallic': self.metallic_suffix.text()
            },
            'advanced': {
                'export_log': self.export_log_checkbox.isChecked(),
                'dark_theme': self.dark_theme_checkbox.isChecked(),
                'play_sound': self.sound_checkbox.isChecked()
            }
        }
        self.settings.save_settings(current_settings)

    def _select_folder(self):
        """Open folder selection dialog"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Folder",
            self.folder_path_edit.text()
        )
        if folder:
            self.folder_path_edit.setText(folder)
            self._save_settings()

    def _start_packing(self):
        """Start the packing process with validation"""
        folder = self.folder_path_edit.text().strip()
        if not self._validate_folder(folder):
            return

        self._prepare_for_packing()

        suffixes = {
            'ao': self.ao_suffix.text(),
            'roughness': self.roughness_suffix.text(),
            'metallic': self.metallic_suffix.text()
        }
        log_to_file = self.export_log_checkbox.isChecked()

        self.worker = PackerWorker(folder, suffixes, log_to_file, self.signals)
        self._start_worker_thread()

    def _validate_folder(self, folder: str) -> bool:
        """Validate the selected folder path"""
        if not folder or not os.path.isdir(folder):
            self._handle_log_output(
                '<span style="color:orange">⚠️ Please select a valid folder before starting.</span>'
            )
            return False
        return True

    def _prepare_for_packing(self):
        """Prepare UI for packing process"""
        self.pack_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.log_output.clear()
        self.progress_bar.setValue(0)
        self.packed_files_count = 0

    def _start_worker_thread(self):
        """Start the worker thread safely"""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()

        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker_thread.start()
        self._save_settings()

    def _cancel_packing(self):
        """Cancel the current packing operation"""
        if hasattr(self, "worker"):
            self.worker.stopped = True
        self.pack_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self._handle_log_output(
            '<span style="color:black">⚠️ Packing <b>cancelled</b> by user. '
            'Finalizing packing of last texture in progress...</span>'
        )

    def _handle_finished_count(self, count: int):
        """Handle completion with file count"""
        self.packed_files_count = count
        if count == 0:
            self._handle_log_output(
                '<span style="color:orange">⚠️ <b>No files were packed.</b></span>'
            )
        else:
            self._handle_log_output(
                f'<span style="color:green">🎉 <b>{count}</b> files packed successfully.</span>'
            )

    def _finish_packing(self):
        """Clean up after packing completes"""
        self.pack_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setValue(100)

        if not hasattr(self, "packed_files_count") or self.packed_files_count == 0:
            self._handle_log_output(
                '<span style="color:orange">⚠️ No files matched the suffixes. Nothing packed.</span>'
            )
        else:
            self._handle_log_output(
                '<span style="color:green">🎉 Packing process <b>finished</b>.</span>'
            )

        if self.sound_checkbox.isChecked():
            self._play_done_sound()

        self._cleanup_worker_thread()

    def _cleanup_worker_thread(self):
        """Safely clean up worker thread"""
        if hasattr(self, "worker_thread"):
            self.worker_thread.quit()
            self.worker_thread.wait()
            self.worker_thread = None

    def _handle_log_output(self, message: Union[str, Tuple[str, str]]):
        """Handle log output with optional color formatting"""
        if isinstance(message, tuple):
            text, color = message
            self.log_output.append(f'<span style="color:{color}">{text}</span>')
        else:
            self.log_output.append(message)
        self.log_output.ensureCursorVisible()

    def _play_done_sound(self):
        """Play completion sound if enabled"""
        base_dir = Path(__file__).parent
        sound_path = resource_path('resources/done.wav')
        self.sound_player.play(sound_path)
        path = base_dir / '..' / 'resources' / 'done.wav'
        self.sound_player.play(str(path.resolve()))

    @staticmethod
    def _show_manual():
        """Open the user manual in default browser"""
        webbrowser.open("https://github.com/Sergey-Russiyan/ORM_Packer/blob/main/README.md")

    @staticmethod
    def _open_donation_link():
        """Open donation link in default browser"""
        webbrowser.open("https://buymeacoffee.com/badgamesokt")

    @staticmethod
    def _open_email_client():
        """Open email client with feedback template"""
        email = "bad.games.ok@gmail.com"
        subject = "Feedback for Texture Packer App"
        body = "Hi,\n\nI wanted to share the following feedback:\n\n"

        # Gmail compose URL
        gmail_url = (
            f"https://mail.google.com/mail/?view=cm&fs=1"
            f"&to={email}"
            f"&su={subject}"
            f"&body={body}"
        )
        webbrowser.open(gmail_url)

    def dragEnterEvent(self, event):
        """Handle drag enter event for folder dropping"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """Handle folder drop event"""
        urls = event.mimeData().urls()
        if urls:
            local_path = urls[0].toLocalFile()
            if os.path.isdir(local_path):
                self.folder_path_edit.setText(local_path)
                self._save_settings()


class DelayedTooltipButton(QPushButton):
    """Custom button with delayed tooltip functionality"""

    def __init__(
            self,
            text: str,
            tooltip_key: Optional[str] = None,
            delay_ms: int = 1000,
            resource_manager: Optional[ResourceManager] = None,
            parent: Optional[QWidget] = None
    ):
        super().__init__(text, parent)
        self._delay_ms = delay_ms
        self._tooltip_key = tooltip_key
        self._resource_manager = resource_manager
        self._tooltip_text = self._get_tooltip_text()
        self._init_timer()

    def _get_tooltip_text(self) -> Optional[str]:
        """Get tooltip text from resource manager if available"""
        if self._tooltip_key and self._resource_manager:
            return self._resource_manager.get(self._tooltip_key, "Tooltip not found")
        return None

    def _init_timer(self):
        """Initialize the tooltip timer"""
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._show_tooltip)

    def enterEvent(self, event):
        """Handle mouse enter event to start tooltip timer"""
        super().enterEvent(event)
        if self._tooltip_text:
            self._timer.start(self._delay_ms)

    def leaveEvent(self, event):
        """Handle mouse leave event to hide tooltip"""
        super().leaveEvent(event)
        if self._timer.isActive():
            self._timer.stop()
            QToolTip.hideText()

    def _show_tooltip(self):
        """Display the tooltip at the bottom center of the button"""
        if self._tooltip_text:
            QToolTip.showText(
                self.mapToGlobal(QPoint(self.width() // 2, self.height())),
                self._tooltip_text,
                self
            )


class ResourceManager:
    """Manages localized resources and tooltips"""

    def __init__(self, resource_file: str):
        with open(resource_file, encoding='utf-8') as f:
            self.data = json.load(f)

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a resource string by key"""
        return self.data.get(key, default)