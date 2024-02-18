import ctypes
import sys

from pydantic import BaseModel
from qt_settings import PathQuery, QInfluxConfigWidget, QPathSelector
from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtWidgets import QApplication, QWidget


class StringConfig(QWidget):
    class Model(BaseModel):
        value: int = 0
        default: str = "test"

        class Config:
            arbitrary_types_allowed = True

    changed = QtCore.Signal(Model)

    def __init__(self):
        super().__init__()

        self._data = self.Model(default="Hello ")

        self.value_spin = QtWidgets.QSpinBox()
        self.value_spin.setValue(self._data.value)
        self.value_spin.valueChanged.connect(self._on_value_changed)

        self.default = QtWidgets.QLineEdit()
        self.default.setText(self._data.default)
        self.default.textChanged.connect(self._on_value_changed)
        self.default.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(r"[^\s]+")))

        self._layout = QtWidgets.QFormLayout()
        self._layout.addRow("Value", self.value_spin)
        self._layout.addRow("Default", self.default)

        self.setLayout(self._layout)

    def _on_value_changed(self, value):
        self.changed.emit(self.data)

    @property
    def data(self) -> Model:
        return StringConfig.Model(value=self.value_spin.value(), default=self.default.text())

    @data.setter
    def data(self, value: Model) -> None:
        self.value_spin.setValue(value.value)
        self.default.setText(value.default)


def encapsulate_groupbox(widget: QWidget, title: str) -> QWidget:
    groupbox = QtWidgets.QGroupBox(title)
    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(widget)
    groupbox.setLayout(layout)
    return groupbox


class TestConfig(QWidget):
    class Model(BaseModel):
        path: QPathSelector.PathModel
        value1: StringConfig.Model
        value2: StringConfig.Model
        influx: QInfluxConfigWidget.Model

    changed = QtCore.Signal(Model)

    def __init__(self):
        super().__init__()

        self.groupbox = QtWidgets.QGroupBox("Test")
        self.value1 = StringConfig()
        self.value2 = StringConfig()
        self.value1.changed.connect(self._on_value_changed)
        self.value2.changed.connect(self._on_value_changed)
        self.infux = QInfluxConfigWidget()
        self.infux.changed.connect(self._on_value_changed)

        self.path = QPathSelector(supported_types="*.lock", type=PathQuery.LoadSaveEnum.EXISTING_DIRECTORY)
        self.path.changed.connect(self._on_value_changed)

        self._layout = QtWidgets.QFormLayout()
        self._layout.addRow("Value1", self.value1)
        self._layout.addRow("Value2", self.value2)
        self._layout.addRow("Path", self.path)
        self._layout.addRow(encapsulate_groupbox(self.infux, "Influx"))
        self.groupbox.setLayout(self._layout)

        self._layout = QtWidgets.QVBoxLayout()
        self._layout.addWidget(self.groupbox)
        self.setLayout(self._layout)

    def _on_value_changed(self, value):
        self.changed.emit(self.data)

        # schema = self._data.model()

    @property
    def data(self) -> Model:
        return TestConfig.Model(
            value1=self.value1.data, value2=self.value2.data, path=self.path.data, influx=self.infux.data
        )

    @data.setter
    def data(self, value: Model) -> None:
        self.value1.data = value.value1
        self.value2.data = value.value2
        self.path.data = value.path
        self.infux.data = value.influx
        # self._data = self.Model(value=StringConfig.Model(value=0, default='Hello '),

        # self.value = StringConfig()
        # self.value.value_spin.setValue(self._data.value.value)
        # self.value.value_spin.valueChanged.connect(self._on_value_changed)

        # self._layout = QtWidgets.QFormLayout()
        # self._layout.addRow('Value', self.value)

        # self.setLayout(self._layout)


# class QConfigViewer(QWidget):
#     def __init__(self):

#         pass


if __name__ == "__main__":

    app = QApplication([])

    widget = TestConfig()
    widget.changed.connect(lambda x: print("change", x))
    widget.show()
    app.exec_()
