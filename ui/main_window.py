from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                               QPushButton, QLabel, QTextEdit, QProgressBar,
                               QGroupBox, QCheckBox, QFileDialog)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QThread
from worker.packer_worker import PackerWorker
from settings.settings_manager import SettingsManager
from PySide6.QtCore import QFile, QTextStream
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QPushButton, QToolTip
from PySide6.QtCore import QTimer, QPoint
from PySide6.QtWidgets import QSizePolicy, QGridLayout
from PySide6.QtCore import QSize

import webbrowser
import os
import json

class TexturePackerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = SettingsManager()

        self.worker_thread = None
        self._init_ui()
        self._load_settings()
        self._setup_connections()

    def _init_ui(self):
        self.setWindowTitle("ORM Texture Packer")
        self.resize(720, 540)
        self.setAcceptDrops(True)

        # Create all UI elements
        self._create_folder_ui()
        self._create_suffix_ui()
        self._create_log_ui()
        self._create_advanced_ui()
        buttons_container = self._create_buttons()  # Get the container widget

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
        resources_path = os.path.join("resources/i18n", "tooltips_en.json")
        resource_manager = ResourceManager(resources_path)

        self.folder_layout = QHBoxLayout()
        self.folder_path_edit = QLineEdit()
        self.folder_button = QPushButton()
        self.folder_button = DelayedTooltipButton("📁", "exp_button_t", delay_ms=1000,
                                                resource_manager=resource_manager)
        self.folder_clear_button = DelayedTooltipButton("❌", "clear_button_t", delay_ms=1000,
                                                  resource_manager=resource_manager)


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
        resources_path = os.path.join("resources/i18n", "tooltips_en.json")
        resource_manager = ResourceManager(resources_path)
        # Advanced options toggle button
        self.advanced_button = DelayedTooltipButton("Advanced Options ▼", "adv_opt_button_t", delay_ms=1000,
                                                  resource_manager=resource_manager)
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
        resources_path = os.path.join("resources/i18n", "tooltips_en.json")
        resource_manager = ResourceManager(resources_path)

        # Main buttons container
        buttons_container = QWidget()
        buttons_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        main_layout = QHBoxLayout(buttons_container)
        main_layout.setSpacing(10)  # Fixed spacing between sections
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 1. Start Button Section (1/3 width)
        start_container = QWidget()
        start_layout = QHBoxLayout(start_container)
        start_layout.setContentsMargins(0, 0, 0, 0)

        self.pack_button = DelayedTooltipButton("🔄 Start Pack", "pack_button_t", delay_ms=1000,
                                                  resource_manager=resource_manager)

        self.pack_button.setFixedHeight(60)  # Fixed 2x height
        start_layout.addWidget(self.pack_button)
        main_layout.addWidget(start_container, stretch=1)  # 1/3 width

        # 2. Right Buttons Section (2/3 width total)
        right_container = QWidget()
        right_layout = QHBoxLayout(right_container)
        right_layout.setSpacing(10)  # Fixed spacing between button columns
        right_layout.setContentsMargins(0, 0, 0, 0)

        # First column (1/3 width)
        col1 = QWidget()
        col1_layout = QVBoxLayout(col1)
        col1_layout.setSpacing(5)
        self.cancel_button = QPushButton()
        self.cancel_button = DelayedTooltipButton("✋ Cancel", "cancel_button_t", delay_ms=1000,
                                                  resource_manager=resource_manager)
        self.manual_button = DelayedTooltipButton("📖 Manual", "manual_button_t", delay_ms=1000,
                                                  resource_manager=resource_manager)
        for btn in [self.cancel_button, self.manual_button]:
            btn.setFixedHeight(30)  # Normal height
        col1_layout.addWidget(self.cancel_button)
        col1_layout.addWidget(self.manual_button)
        right_layout.addWidget(col1, stretch=1)  # 1/3 width

        # Second column (1/3 width)
        col2 = QWidget()
        col2_layout = QVBoxLayout(col2)
        col2_layout.setSpacing(5)

        self.buy_button = DelayedTooltipButton("☕ Buy me a Coffee", "coffee_button_t", delay_ms=1000,
                                                  resource_manager=resource_manager)
        self.feedback_button = DelayedTooltipButton("📧 Write Email", "email_button_t", delay_ms=1000,
                                               resource_manager=resource_manager)

        for btn in [self.buy_button, self.feedback_button]:
            btn.setFixedHeight(30)  # Normal height
        col2_layout.addWidget(self.buy_button)
        col2_layout.addWidget(self.feedback_button)
        right_layout.addWidget(col2, stretch=1)  # 1/3 width

        main_layout.addWidget(right_container, stretch=2)  # 2/3 width total

        return buttons_container

    def _load_settings(self):
        settings = self.settings.load_settings()
        dark_theme = bool(settings['advanced']['dark_theme'])
        print(f"Initial theme setting: {settings['advanced']['dark_theme']}")
        print(f"Loading settings - dark_theme: {dark_theme}")  # Debug print

        self.dark_theme_checkbox.setChecked(dark_theme)
        self._apply_theme(dark_theme)  # call once

        self.folder_path_edit.setText(settings['folder'])
        self.ao_suffix.setText(settings['suffixes']['ao'])
        self.roughness_suffix.setText(settings['suffixes']['roughness'])
        self.metallic_suffix.setText(settings['suffixes']['metallic'])

        self.export_log_checkbox.setChecked(settings['advanced']['export_log'])
        self.sound_checkbox.setChecked(settings['advanced']['play_sound'])

    def _setup_connections(self):
        self.folder_button.clicked.connect(self._select_folder)
        self.folder_clear_button.clicked.connect(lambda: self.folder_path_edit.setText(""))
        self.pack_button.clicked.connect(self._start_packing)
        self.cancel_button.clicked.connect(self._cancel_packing)
        self.manual_button.clicked.connect(self._show_manual)
        self.buy_button.clicked.connect(self._open_donation_link)
        self.feedback_button.clicked.connect(self._open_email_client)
        self.advanced_button.clicked.connect(self._toggle_advanced_options)

        self.dark_theme_checkbox.stateChanged.connect(self._handle_theme_change)
        #self.dark_theme_checkbox.stateChanged.connect(self.on_dark_theme_state_changed)

    def _handle_theme_change(self, state: int):
        print(f"Theme checkbox changed. State: {state}")
        if state == Qt.Checked:
            print("Applying dark theme")
            self._apply_theme(True)
        elif state == Qt.Unchecked:
            print("Applying light theme")
            self._apply_theme(False)
        else:
            print("Checkbox in partially checked state (ignored)")

    def _toggle_advanced_options(self):
        visible = self.advanced_button.isChecked()
        self.advanced_options_group.setVisible(visible)
        self.advanced_button.setText("Advanced Options ▲" if visible else "Advanced Options ▼")

    def on_dark_theme_state_changed(self, state: int):
        print(f"Theme change requested. State: {state}")
        if state == Qt.Checked:
            self._apply_theme(True)  # dark theme
        elif state == Qt.Unchecked:
            self._apply_theme(False)  # light theme
        else:
            # Optionally handle partially checked or ignore
            pass

    def on_dark_theme_state_changed(self, state: int):
        print(f"on_dark_theme_state_changed called with state: {state}")
        if state == Qt.Checked:
            self._apply_theme(True)
        elif state == Qt.Unchecked:
            self._apply_theme(False)

    def _apply_theme(self, dark_theme: bool):
        """Properly apply theme with full widget refresh"""
        try:
            # Get the absolute path to resources
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            theme_file = "dark_theme.qss" if dark_theme else "light_theme.qss"
            theme_path = os.path.join(base_dir, "resources", theme_file)

            print(f"Expected theme file path: {theme_path}")
            print(f"Exists? {os.path.exists(theme_path)}")
            print(f"Loading theme from: {theme_path}")

            if os.path.exists(theme_path):
                with open(theme_path, "r", encoding='utf-8') as f:
                    stylesheet = f.read()
                    print(f"Read {len(stylesheet)} bytes from stylesheet")

                # Append your QWidget background/color overrides here
                if dark_theme:
                    stylesheet += "\n QWidget { background-color: #222; color: #eee; }"
                else:
                    stylesheet += "\n QWidget { background-color: #fff; color: #000; }"

                app = QApplication.instance()
                app.setStyle("Fusion")
                app.setStyleSheet("")  # Clear old style
                QApplication.processEvents()
                # Apply new style (with appended QWidget rule)
                app.setStyleSheet(stylesheet)
                print(f"Set {'dark' if dark_theme else 'light'} theme stylesheet")

                # Force refresh all widgets
                for widget in app.allWidgets():
                    widget.style().unpolish(widget)
                    widget.style().polish(widget)
                    widget.update()

                print(f"Successfully applied {'dark' if dark_theme else 'light'} theme")
            else:
                print(f"Theme file not found at: {theme_path}")
        except Exception as e:
            print(f"Error applying theme: {str(e)}")

    def _save_settings(self):
        """Centralized method to save all current settings"""
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
        print(f"Saving settings. Dark theme: {current_settings['advanced']['dark_theme']}")
        self.settings.save_settings(current_settings)  # Now calls the public method

    def _select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", self.folder_path_edit.text())
        if folder:
            self.folder_path_edit.setText(folder)
            self._save_settings()

    def _start_packing(self):
        folder = self.folder_path_edit.text()
        if not folder or not os.path.isdir(folder):
            self.log_output.append('<span style="color:red">Please select a valid folder before starting.</span>')
            return

        suffixes = {
            'ao': self.ao_suffix.text(),
            'roughness': self.roughness_suffix.text(),
            'metallic': self.metallic_suffix.text()
        }
        log_to_file = self.export_log_checkbox.isChecked()

        self.pack_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.log_output.clear()
        self.progress_bar.setValue(0)

        self.worker = PackerWorker(folder, suffixes, log_to_file)
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)

        self.worker.progress.connect(self._handle_log_output)
        self.worker.progress_percent.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self._finish_packing)

        self.worker_thread.started.connect(self.worker.run)
        self.worker_thread.start()

        self._save_settings()

    def _cancel_packing(self):
        if hasattr(self, "worker"):
            self.worker.stopped = True
        self.pack_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.log_output.append('<span style="color:orange">Packing cancelled by user.</span>')

    def _finish_packing(self):
        self.pack_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setValue(100)
        self.log_output.append('<span style="color:green">Packing process finished.</span>')

        if self.sound_checkbox.isChecked():
            # Sound implementation would go here
            pass

        if hasattr(self, "worker_thread"):
            self.worker_thread.quit()
            self.worker_thread.wait()

    def _handle_log_output(self, message):
        if isinstance(message, tuple):
            text, color = message
            self.log_output.append(f'<span style="color:{color}">{text}</span>')
        else:
            self.log_output.append(message)
        self.log_output.ensureCursorVisible()

    def _show_manual(self):
        webbrowser.open("https://hallowed-car-2d0.notion.site/Texture-Packer-Manual-1f43ce421cf1808fb943fbfe6a93d716")

    def _open_donation_link(self):
        webbrowser.open("https://buymeacoffee.com/badgamesokt")

    def _open_email_client(self):
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

        # Open in default browser (should be Chrome for most users)
        webbrowser.open(gmail_url)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            local_path = urls[0].toLocalFile()
            if os.path.isdir(local_path):
                self.folder_path_edit.setText(local_path)
                self._save_settings()

class DelayedTooltipButton(QPushButton):
    def __init__(self, text, tooltip_key=None, delay_ms=1000, resource_manager=None, parent=None):
        super().__init__(text, parent)
        self._delay_ms = delay_ms
        self._tooltip_key = tooltip_key
        self._resource_manager = resource_manager

        # Set tooltip text if resource manager and key are provided
        if self._tooltip_key and self._resource_manager:
            self._tooltip_text = self._resource_manager.get(self._tooltip_key, "Tooltip not found")
        else:
            self._tooltip_text = None

        # Timer for delayed tooltip
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._show_tooltip)

    def enterEvent(self, event):
        super().enterEvent(event)
        if self._tooltip_text:
            self._timer.start(self._delay_ms)

    def leaveEvent(self, event):
        super().leaveEvent(event)
        if self._timer.isActive():
            self._timer.stop()
            QToolTip.hideText()

    def _show_tooltip(self):
        if self._tooltip_text:
            QToolTip.showText(self.mapToGlobal(QPoint(self.width() // 2, self.height())), self._tooltip_text, self)

class ResourceManager:
    def __init__(self, resource_file):
        with open(resource_file, encoding='utf-8') as f:
            self.data = json.load(f)

    def get(self, key, default=None):
        return self.data.get(key, default)