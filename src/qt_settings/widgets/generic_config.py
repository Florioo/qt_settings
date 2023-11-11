from pydantic import BaseModel
from PySide2 import QtCore
from PySide2.QtWidgets import QWidget


class QGenericSettingsWidget(QWidget):
    class Model(BaseModel):
        pass

    changed = QtCore.Signal(object)

    def __init__(self) -> None:
        super().__init__()

    @property
    def data(self) -> Model:
        raise NotImplementedError()

    @data.setter
    def data(self, value: Model) -> None:
        del value
        raise NotImplementedError()

    def _on_value_changed(self, value):
        self.changed.emit(self.data)
