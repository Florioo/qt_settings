from PySide2.QtWidgets import QApplication, QLabel, QWidget


def show_widget(widget: QWidget):
    app = QApplication([])
    widget.show()
    app.exec_()


if __name__ == "__main__":
    show_widget(QLabel("Hello World!"))
