from pydantic import BaseModel, Field
from PySide2 import QtWidgets
from PySide2.QtWidgets import QStyle, QToolButton

from .generic_config import QGenericSettingsWidget
from .path.path_query import PathQuery


class QPathSelector(QGenericSettingsWidget):
    class PathModel(BaseModel):
        path: str = Field(max_length=100)

    def __init__(self, supported_types: str, type: PathQuery.LoadSaveEnum, manually_editable: bool = True):
        super().__init__()

        self.path_query = PathQuery(
            parent=self,
            settings=None,
            save_name="",
            supported_types=supported_types,
        )
        self.type = type

        self._data = self.PathModel(path="")

        self.path = QtWidgets.QLineEdit()
        self.path.setText(self._data.path)
        self.path.textChanged.connect(self._on_value_changed)

        if not manually_editable:
            self.path.setReadOnly(True)

        self.button = QToolButton()

        self.button.setIcon(self.style().standardIcon(QStyle.SP_DirIcon))
        self.button.clicked.connect(self._on_button_clicked)

        self._layout = QtWidgets.QHBoxLayout()
        self._layout.addWidget(self.path)
        self._layout.addWidget(self.button)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self._layout)

    def _on_button_clicked(self):
        selected_path = self.path_query.get_path(self.type)
        self.path.setText(selected_path)

    @property
    def data(self) -> PathModel:
        return QPathSelector.PathModel(path=self.path.text())

    @data.setter
    def data(self, value: PathModel) -> None:
        self.path.setText(value.path)
