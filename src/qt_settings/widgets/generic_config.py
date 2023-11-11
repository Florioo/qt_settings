from typing import Optional

from pydantic import BaseModel, Field
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import QSettings
from PySide2.QtWidgets import QApplication, QFileDialog, QStyle, QToolButton, QWidget
import influxdb_client
import influxdb_client.rest
import urllib3.exceptions

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
    
