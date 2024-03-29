import json
import logging
from typing import Dict

from qt_utils import messaging
from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtWidgets import QWidget

from .widgets import PathQuery, QGenericSettingsWidget


class ConfigDialog(QtWidgets.QDialog):
    configs: Dict[str, QGenericSettingsWidget]
    block_signals: bool = False

    def __init__(self, parent: QWidget, settings: QtCore.QSettings):
        super().__init__(parent)
        self.settings = settings
        self.path_query = PathQuery(self, settings, "test", "*.json")

        self.setWindowTitle("Configuration")
        self.resize(400, 300)
        self.log = logging.getLogger(__name__)
        # Create a import/export widget
        import_button = QtWidgets.QPushButton("Import")
        export_button = QtWidgets.QPushButton("Export")
        import_button.clicked.connect(self.load_from_file)
        export_button.clicked.connect(self.save_to_file)
        self._import_export_layout = QtWidgets.QHBoxLayout()
        self._import_export_layout.addWidget(import_button)
        self._import_export_layout.addWidget(export_button)
        self._import_export_layout.addStretch(1)
        self._import_export_layout.setContentsMargins(0, 0, 0, 0)

        # Add Tabwidget
        self._tab_widget = QtWidgets.QTabWidget()
        self._layout = QtWidgets.QVBoxLayout()
        self._layout.addLayout(self._import_export_layout)
        self._layout.addWidget(self._tab_widget)
        self.setLayout(self._layout)

        self.configs = {}

    def to_json(self) -> str:
        data = {}
        for name, config in self.configs.items():
            data[name] = config.data.model_dump()
        return json.dumps(data)

    def from_json(self, data: str) -> None:
        data = json.loads(data)
        for name, config in self.configs.items():
            if name in data:
                try:
                    config.data = config.data.model_validate(data[name])  # type: ignore
                except Exception as e:
                    print(e)
        self.log.info("Loaded config from settings")

    @messaging.catch_exception("Failed to load config from file")
    def load_from_file(self):
        path = self.path_query.get_path(PathQuery.LoadSaveEnum.LOAD_FILE)

        if path is None:
            return

        with open(path, "r") as f:
            self.from_json(f.read())
        self.log.info(f"Loaded config from {path}")

    @messaging.catch_exception("Failed to save config to file")
    def save_to_file(self):
        path = self.path_query.get_path(PathQuery.LoadSaveEnum.SAVE_FILE)

        if path is None:
            return

        with open(path, "w") as f:
            f.write(self.to_json())
        self.log.info(f"Saved config to {path}")

    @messaging.catch_exception("Failed to load default config")
    def load_default(self):
        for config in self.configs.values():
            config.from_default()
        self.log.info("Loaded default config")

    def save_to_settings(self):
        self.settings.setValue("config", self.to_json())
        self.log.info("Saved config to settings")

    def load_from_settings(self):
        self.block_signals = True
        data = self.settings.value("config", None, str)
        if data is None or not isinstance(data, str) or data == "":
            self.log.error("Failed to load config from settings")
            self.load_default()
        else:
            self.from_json(data)
        self.block_signals = False
        self.save_to_settings()

    def open(self):
        self.show()

    def add_widget(self, name: str, widget: QGenericSettingsWidget):
        # Check if sublass is QGenericSettingsWidget
        assert isinstance(widget, QGenericSettingsWidget)

        self.configs[name] = widget
        widget.changed.connect(self.data_changed)
        self._tab_widget.addTab(widget, name)

    def data_changed(self):
        if self.block_signals:
            return

        self.save_to_settings()

    def get_menuaction(self) -> QtGui.QAction:
        action = QtGui.QAction("Settings", self)
        action.triggered.connect(self.open)
        return action
