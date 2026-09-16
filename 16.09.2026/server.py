import socket
import threading
from protocol import recv_exact, send_message


clients = {}
clients_lock = threading.Lock()

def  broadcast(command, payload, owner = None):
    with clients_lock:
        target_sock = list(clients.keys())
    for sock in target_sock:
        if sock == owner:
            continue
        try:
            send_message(sock, command, payload)
        except (ConnectionError, OSError):
            print("Не удалось доставить сообщение клиенту")

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 1000))
    server_socket.listen()
    print("Сервер запущен")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            thread = threading.Thread(args=(client_socket,addr), daemon=True)
            thread.start()
    except KeyboardInterrupt:
        print("Сервер остановлен по запросу оператора")
    finally:
        server_socket.close()

if __name__ == '__main__':
    main()
