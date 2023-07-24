import sys
from PySide6 import QtWebSockets, QtCore, QtWidgets
from helpers.get_websocket_server_settings import get_websocket_server_settings


class Client(QtCore.QObject):
    def __init__(self, parent):
        super().__init__(parent)

        self.client = QtWebSockets.QWebSocket("", QtWebSockets.QWebSocketProtocol.Version13, None)
        self.client.error.connect(self.on_error)

        self.client.textMessageReceived.connect(self.on_text_msg_received)

        data = get_websocket_server_settings()
        self.client.open(QtCore.QUrl(f"{data[0]}/pyside6_client"))

        print('client should be connected now.')

        self.stacked_layout = QtWidgets.QStackedLayout()
        self.main_widget = QtWidgets.QWidget()
        self.main_widget.setLayout(self.stacked_layout)

        # Add your different pages here
        self.page_1 = QtWidgets.QLabel("Page 1 Content")
        self.page_2 = QtWidgets.QLabel("Page 2 Content")

        # Add the pages to the stacked layout
        self.stacked_layout.addWidget(self.page_1)
        self.stacked_layout.addWidget(self.page_2)

        # Show the initial page (index 0)
        self.stacked_layout.setCurrentIndex(0)

        # Buttons for page switching
        self.button_page_1 = QtWidgets.QPushButton("Page 1")
        self.button_page_2 = QtWidgets.QPushButton("Page 2")

        self.button_page_1.clicked.connect(lambda: self.change_page_within_gui(1))
        self.button_page_2.clicked.connect(lambda: self.change_page_within_gui(2))

        # Layout for buttons and stacked layout
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.button_page_1)
        button_layout.addWidget(self.button_page_2)

        main_layout = QtWidgets.QVBoxLayout(self.main_widget)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(self.stacked_layout)

    @QtCore.Slot(QtWebSockets.QWebSocketProtocol.CloseCode)
    def on_error(self, code):
        print(f'Error occurred, closing client ({code})')
        self.client.close()

    @QtCore.Slot(str)
    def on_text_msg_received(self, message):
        print(f'client received the message: {message}')
        if message.startswith("page_number_"):
            page_number = int(message.split("_")[-1])
            self.change_page_within_gui(page_number)

    def close(self):
        print('closing client')
        self.client.close()

    def send_message(self, message):
        self.client.sendTextMessage(message)

    def change_page_within_gui(self, page_number):
        if 1 <= page_number <= 2:
            self.stacked_layout.setCurrentIndex(page_number - 1)
        else:
            print(f"Invalid page number: {page_number}")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    client = Client(app)

    # Handle application exit and close the WebSocket connection gracefully
    app.aboutToQuit.connect(client.close)

    main_window = QtWidgets.QMainWindow()
    main_window.setCentralWidget(client.main_widget)
    main_window.show()

    sys.exit(app.exec())
