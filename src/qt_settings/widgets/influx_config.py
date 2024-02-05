import influxdb_client
import influxdb_client.rest
import urllib3.exceptions
from pydantic import BaseModel
from qt_utils import messaging
from qtpy import QtWidgets
from qtpy.QtCore import QThread, Signal
from qtpy.QtWidgets import (
    QStyle,
    QToolButton,
)

from .generic_config import QGenericSettingsWidget


class InfluxConfigTestThread(QThread):
    result_signal = Signal(messaging.Result)

    def __init__(self, config: "QInfluxConfigWidget.Model") -> None:
        QThread.__init__(self)
        self.config = config

    def run(self):
        try:
            self.config.test_connection()
            self.config.check_query()

            self.result_signal.emit(messaging.Success(message="Connection successful").to_result())
            pass
        except Exception as e:
            self.result_signal.emit(messaging.Error.from_exception(e).to_result())


class QInfluxConfigWidget(QGenericSettingsWidget):
    class Model(BaseModel):
        url: str
        token: str
        org: str
        bucket: str
        measurement: str
        force_ssl: bool
        debug: bool
        flush_delay: float
        timeout: int

        def get_client(self) -> influxdb_client.InfluxDBClient:
            client = influxdb_client.InfluxDBClient(
                url=self.url,
                token=self.token,
                debug=self.debug,
                timeout=self.timeout,
                org=self.org,
                enable_gzip=True,
                verify_ssl=self.force_ssl,
            )
            return client

        def test_connection(self):
            client = self.get_client()
            try:
                response = client.api_client.request("GET", f"{self.url}/ping")
            except urllib3.exceptions.NameResolutionError as e:
                raise Exception(f"Url does not exist '{self.url}'") from e

            if response.status != 204:
                raise Exception(f"Connection to '{self.url}' failed.")

            return client

        def check_query(self):
            client = self.get_client()
            """Check that the credentials has permission to query from the Bucket"""

            try:
                client.query_api().query(f'from(bucket:"{self.bucket}") |> range(start: -1m) |> limit(n:1)', self.org)
            except influxdb_client.rest.ApiException as e:
                # missing credentials
                if e.status == 404:
                    raise Exception(
                        f"The specified token doesn't have sufficient credentials to "
                        f"read from '{self.bucket}' bucket or specified bucket doesn't exists."
                    ) from e
                if e.status == 401:
                    raise Exception("The specified token is invalid.") from e

                raise e

    test_thread: InfluxConfigTestThread | None = None

    def __init__(self) -> None:
        super().__init__()

        # Standard options
        self.url_input = QtWidgets.QLineEdit()
        self.url_input.textChanged.connect(self._on_value_changed)
        self.token_input = QtWidgets.QLineEdit()
        self.token_input.textChanged.connect(self._on_value_changed)
        self.org_input = QtWidgets.QLineEdit()
        self.org_input.textChanged.connect(self._on_value_changed)
        self.bucket_input = QtWidgets.QLineEdit()
        self.bucket_input.textChanged.connect(self._on_value_changed)
        self.measurement_input = QtWidgets.QLineEdit()
        self.measurement_input.textChanged.connect(self._on_value_changed)

        self.show_advanced_options = QToolButton()
        self.show_advanced_options.setCheckable(True)
        self.show_advanced_options.setChecked(False)
        self.show_advanced_options.setIcon(self.style().standardIcon(QStyle.SP_ArrowDown))
        self.show_advanced_options.clicked.connect(self._update_ui)

        # Advanced options
        self.force_ssl_input = QtWidgets.QCheckBox("Force SSL")
        self.force_ssl_input.stateChanged.connect(self._on_value_changed)

        self.debug_input = QtWidgets.QCheckBox("Debug")
        self.debug_input.stateChanged.connect(self._on_value_changed)

        self.timeout_input = QtWidgets.QSpinBox()
        self.timeout_input.valueChanged.connect(self._on_value_changed)
        self.timeout_input.setRange(0, 600)
        self.timeout_input.setSuffix("s")

        self.flush_delay_input = QtWidgets.QDoubleSpinBox()
        self.flush_delay_input.valueChanged.connect(self._on_value_changed)
        self.flush_delay_input.setRange(0, 600)
        self.flush_delay_input.setSuffix("s")

        # Test button
        self.test_button = QtWidgets.QPushButton("Test config")
        self.test_button.clicked.connect(self._on_test_clicked)

        self.advanced_options = QtWidgets.QGroupBox("Advanced options")
        self.advanced_options.setHidden(True)
        self.advanced_options_layout = QtWidgets.QFormLayout()
        self.advanced_options_layout.addRow("Force SSL", self.force_ssl_input)
        self.advanced_options_layout.addRow("Flush Delay", self.flush_delay_input)
        self.advanced_options_layout.addRow("Timeout", self.timeout_input)
        self.advanced_options_layout.addRow("Debug", self.debug_input)
        self.advanced_options.setLayout(self.advanced_options_layout)

        # Set the layout
        self._layout = QtWidgets.QFormLayout()
        self._layout.addRow("URL", self.url_input)
        self._layout.addRow("Token", self.token_input)
        self._layout.addRow("Org", self.org_input)
        self._layout.addRow("Bucket", self.bucket_input)
        self._layout.addRow("Measurement", self.measurement_input)
        self._layout.addRow("Show advanced", self.show_advanced_options)
        self._layout.addRow(self.advanced_options)
        self._layout.addRow(self.test_button)
        self.setLayout(self._layout)

        self._update_ui()

    def _update_ui(self):
        if self.show_advanced_options.isChecked():
            self.show_advanced_options.setIcon(self.style().standardIcon(QStyle.SP_ArrowUp))
            self.advanced_options.setHidden(False)
        else:
            self.show_advanced_options.setIcon(self.style().standardIcon(QStyle.SP_ArrowDown))
            self.advanced_options.setHidden(True)

        is_running = self.test_thread is not None and self.test_thread.isRunning()

        if is_running:
            self.test_button.setText("Testing...")
        else:
            self.test_button.setText("Check connection")

        self.test_button.setEnabled(not is_running)

    def _on_test_clicked(self):
        if self.test_thread is not None and self.test_thread.isRunning():
            messaging.Error(trace="", error="Test already running").to_result().display(self)
            return

        self.test_thread = InfluxConfigTestThread(self.data)
        self.test_thread.result_signal.connect(lambda result: result.display(self))
        self.test_thread.started.connect(self._update_ui)
        self.test_thread.finished.connect(self._update_ui)
        self.test_thread.start()

    @property
    def data(self) -> Model:
        return self.Model(
            url=self.url_input.text(),
            token=self.token_input.text(),
            org=self.org_input.text(),
            bucket=self.bucket_input.text(),
            measurement=self.measurement_input.text(),
            force_ssl=self.force_ssl_input.isChecked(),
            flush_delay=self.flush_delay_input.value(),
            debug=self.debug_input.isChecked(),
            timeout=self.timeout_input.value() // 1000,
        )

    @data.setter
    def data(self, value: Model) -> None:
        self.url_input.setText(value.url)
        self.token_input.setText(value.token)
        self.org_input.setText(value.org)
        self.bucket_input.setText(value.bucket)
        self.measurement_input.setText(value.measurement)
        self.force_ssl_input.setChecked(value.force_ssl)
        self.flush_delay_input.setValue(value.flush_delay)
        self.debug_input.setChecked(value.debug)
        self.timeout_input.setValue(value.timeout * 1000)
