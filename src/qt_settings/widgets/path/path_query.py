import os
from enum import Enum

from qtpy.QtCore import QSettings
from qtpy.QtWidgets import QFileDialog, QWidget


class PathQuery:
    class LoadSaveEnum(Enum):
        EXISTING_DIRECTORY = 1
        SAVE_DIRECTORY = 2
        SAVE_FILE = 3
        LOAD_FILE = 4

    def __init__(
        self, parent: QWidget, settings: QSettings | None, save_name: str, supported_types: str = "All Files (*)"
    ):
        self._parent = parent
        self.settings = settings
        self.save_name = save_name
        self.supported_types = supported_types

    def get_last_folder(self) -> str:
        if self.settings is None:
            return ""

        last_folder = self.settings.value(self.save_name, "", str)

        if not isinstance(last_folder, str):
            last_folder = ""

        return last_folder

    def store_last_folder(self, folder: str) -> None:
        if self.settings is not None:
            self.settings.setValue(self.save_name, folder)

    def get_path(self, type: LoadSaveEnum, filter: str | None = None) -> str | None:
        last_folder = self.get_last_folder()
        if filter is None:
            filter = self.supported_types
        if type == self.LoadSaveEnum.LOAD_FILE:
            filePath, _ = QFileDialog.getOpenFileName(
                parent=self._parent,
                caption="Open File",
                dir=last_folder,
                filter=filter,
            )

        elif type == self.LoadSaveEnum.SAVE_FILE:
            filePath, _ = QFileDialog.getSaveFileName(
                parent=self._parent,
                caption="Save File",
                dir=last_folder,
                filter=filter,
            )

        elif type == self.LoadSaveEnum.EXISTING_DIRECTORY:
            filePath = QFileDialog.getExistingDirectory(
                parent=self._parent,
                caption="Open Directory",
                dir=last_folder,
            )

        else:
            raise NotImplementedError

        if not filePath:
            return

        filePath: str

        # Remember the folder for next time
        self.store_last_folder(os.path.dirname(filePath))

        return filePath
