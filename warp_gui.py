#!/usr/bin/env python3
import logging
import sys
import subprocess
import time
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QWidget,
)
from PyQt5.QtCore import Qt, QTimer

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
LOGGER = logging.getLogger(__name__)

CHECKING_STATUS_TEXT = "Status: Checking..."
CONNECTED_STATUS_TEXT = "Status: Connected"
DISCONNECTED_STATUS_TEXT = "Status: Disconnected"


class CloudflareWarpGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(5000)  # Update status every 5 seconds

    def initUI(self):
        self.setWindowTitle("Cloudflare WARP")
        self.setGeometry(300, 300, 300, 200)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Status label
        self.status_label = QLabel(CHECKING_STATUS_TEXT)
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)

        # Buttons layout
        button_layout = QHBoxLayout()

        # Connect/Disconnect button
        self.connection_button = QPushButton("Connect")
        self.connection_button.clicked.connect(self.toggle_connection_btn)
        button_layout.addWidget(self.connection_button)
        self.connection_button.setEnabled(False)

        main_layout.addLayout(button_layout)

        # Update status initially
        self.update_status()

    def update_status(self):
        LOGGER.info("Updating status...")
        try:
            result = subprocess.run(
                ["warp-cli", "status"], capture_output=True, text=True, check=True
            )
            if "Connected" in result.stdout:
                LOGGER.info("Connected to WARP")
                self.status_label.setText(CONNECTED_STATUS_TEXT)
                self.status_label.setStyleSheet("color: green;")
                self.connection_button.setText("Disconnect")
            else:
                LOGGER.info("Disconnected from WARP")
                self.status_label.setText(DISCONNECTED_STATUS_TEXT)
                self.status_label.setStyleSheet("color: red;")
                self.connection_button.setText("Connect")
            self.connection_button.setEnabled(True)
        except subprocess.CalledProcessError:
            LOGGER.error("Error checking WARP status")
            self.status_label.setText("Status: Error checking WARP status")
            self.status_label.setStyleSheet("color: orange;")
        except FileNotFoundError:
            LOGGER.error("warp-cli not found")
            self.status_label.setText("Status: WARP CLI not found")
            self.status_label.setStyleSheet("color: red;")
            self.connection_button.setEnabled(False)

    def connect_warp(self):
        try:
            LOGGER.info("Connecting to WARP...")
            subprocess.run(["warp-cli", "connect"], check=True)
            self.update_status()
        except (subprocess.CalledProcessError, FileNotFoundError):
            LOGGER.error("Error connecting to WARP")
            self.status_label.setText("Error: Could not connect to WARP")
            self.status_label.setStyleSheet("color: red;")

    def disconnect_warp(self):
        try:
            LOGGER.info("Disconnecting from WARP...")
            subprocess.run(["warp-cli", "disconnect"], check=True)
            self.update_status()
        except (subprocess.CalledProcessError, FileNotFoundError):
            LOGGER.error("Error disconnecting from WARP")
            self.status_label.setText("Error: Could not disconnect from WARP")
            self.status_label.setStyleSheet("color: red;")

    def toggle_connection_btn(self):
        LOGGER.info("Toggling connection...")
        LOGGER.info("Current connection status: %s", self.is_connected)

        if self.is_connected is True:
            self.disconnect_warp()
        elif self.is_connected is False:
            self.connect_warp()

        self.connection_button.setEnabled(True)

    @property
    def is_connected(self) -> bool:
        return self.status_label.text() == CONNECTED_STATUS_TEXT


def main():
    app = QApplication(sys.argv)
    window = CloudflareWarpGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
