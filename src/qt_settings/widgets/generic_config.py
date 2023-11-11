from pydantic import BaseModel
from PySide2 import QtCore
from PySide2.QtWidgets import QWidget


class QGenericSettingsWidget(QWidget):
    class Model(BaseModel):
        pass

    changed = QtCore.Signal(Model)

    def __init__(self) -> None:
        super().__init__()

    @property
    def data(self) -> Model:
        raise NotImplementedError()

    @data.setter
    def data(self, value: Model) -> None:
        del value
        raise NotImplementedError()
