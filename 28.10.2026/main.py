import json
import socket
import struct
import sys
from queue import Queue

from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


HOST = "127.0.0.1"
PORT = 50505


class NetCom:
    def __init__(self, sock):
        self.sock = sock

    @staticmethod
    def _recv_exact(sock, size):
        chunks = []
        received = 0
        while received < size:
            chunk = sock.recv(size - received)
            if not chunk:
                return None
            chunks.append(chunk)
            received += len(chunk)
        return b"".join(chunks)

    def recv(self):
        header = self._recv_exact(self.sock, 4)
        if header is None:
            return None

        payload_size = struct.unpack("!I", header)[0]
        payload = self._recv_exact(self.sock, payload_size)
        if payload is None:
            return None

        return json.loads(payload.decode("utf-8"))

    def send(self, message):
        payload = json.dumps(message, ensure_ascii=False).encode("utf-8")
        header = struct.pack("!I", len(payload))
        self.sock.sendall(header + payload)


class ReceiveThread(QThread):
    message_received = pyqtSignal(dict)
    connection_lost = pyqtSignal(str)

    def __init__(self, net):
        super().__init__()
        self.net = net
        self._running = True

    def stop(self):
        # вызывается при закрытии окна: после этого потеря соединения не сообщается
        self._running = False

    def run(self):
        while self._running:
            try:
                message = self.net.recv()
            except (OSError, ValueError, struct.error) as exc:
                if self._running:
                    self.connection_lost.emit(str(exc))
                return

            if message is None:
                # сервер закрыл соединение без исключения
                if self._running:
                    self.connection_lost.emit("Сервер закрыл соединение")
                return

            self.message_received.emit(message)


class SendThread(QThread):
    connection_lost = pyqtSignal(str)

    def __init__(self, net):
        super().__init__()
        self.net = net
        self.queue = Queue()

    def send(self, message):
        self.queue.put(message)

    def stop(self):
        # None будит поток, ожидающий в queue.get(), и завершает цикл
        self.queue.put(None)

    def run(self):
        while True:
            message = self.queue.get()
            if message is None:
                break

            try:
                self.net.send(message)
            except OSError as exc:
                self.connection_lost.emit(str(exc))
                break


class MainWindow(QMainWindow):
    def __init__(self, net):
        super().__init__()
        self.net = net

        self.setWindowTitle("PyQt6 network chat")
        self.resize(560, 420)

        self.history = QTextEdit()
        self.history.setReadOnly(True)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Type a message…")

        self.send_button = QPushButton("Send")
        self.status_label = QLabel("Connected")
        self.connected = True

        input_row = QHBoxLayout()
        input_row.addWidget(self.input)
        input_row.addWidget(self.send_button)

        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.history)
        layout.addLayout(input_row)

        root = QWidget()
        root.setLayout(layout)
        self.setCentralWidget(root)

        self.send_button.clicked.connect(self.on_send_clicked)
        self.input.returnPressed.connect(self.on_send_clicked)

        self.receive_thread = ReceiveThread(self.net)
        self.receive_thread.message_received.connect(self.handle_message)
        self.receive_thread.connection_lost.connect(self.on_connection_lost)
        self.receive_thread.start()

        self.send_thread = SendThread(self.net)
        self.send_thread.connection_lost.connect(self.on_connection_lost)
        self.send_thread.start()

    def on_send_clicked(self):
        text = self.input.text().strip()
        if not text:
            return

        self.send_thread.send({
            "type": "chat",
            "text": text,
        })

        self.input.clear()

    def handle_message(self, message):
        if message.get("type") == "chat":
            text = message.get("text", "")
            self.history.append(text)

    def on_connection_lost(self, reason):
        if not self.connected:
            return
        self.connected = False

        self.status_label.setText("Disconnected")
        self.history.append(f"Соединение потеряно: {reason}")
        self.input.setEnabled(False)
        self.send_button.setEnabled(False)

        # останавливаем отправляющий поток, читающий поток уже завершился сам
        self.send_thread.stop()

    def closeEvent(self, event):
        self.receive_thread.stop()
        self.send_thread.stop()

        # закрываем сокет, чтобы разбудить recv() в ReceiveThread
        try:
            self.net.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass

        self.send_thread.wait(2000)
        self.receive_thread.wait(2000)
        event.accept()


def main():
    app = QApplication(sys.argv)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, PORT))
    except OSError as exc:
        print(f"Could not connect to server at {HOST}:{PORT}: {exc}")
        print("Run server.py first, then start main.py.")
        return

    net = NetCom(sock)
    window = MainWindow(net)
    window.show()

    exit_code = app.exec()

    try:
        sock.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass
    sock.close()
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
