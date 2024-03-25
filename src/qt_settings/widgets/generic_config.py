from pydantic import BaseModel
from qtpy import QtCore
from qtpy.QtWidgets import QWidget


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

    def _on_value_changed(self, *args, **kwargs):
        self.changed.emit(self.data)

    def from_default(self):
        self.data = self.Model()