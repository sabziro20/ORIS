import ntpath

import protocol as proto
import socket
import threading


HOST = '0.0.0.0'
PORT = 5555

clients = {}
clients_lock = threading.Lock()
tasks = {}
tasks_lock = threading.Lock()

def broadcast(command, text, exclude = None):
    payload = text.encode('utf-8')
    with clients_lock:
        targets = [s for s in clients if s != exclude]
    for sock in targets:
        try:
            proto.send_message(sock, command, payload)
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass

def handle_client(sock, addr):
    username = None
    try:
        first = proto.recv_message(sock)
        if first is None or first[0] != 'JOIN':
            proto.send_message(sock, 'ERRO', b'first command must be JOIN')
            return

        username = first[1].decode('utf-8', errors='replace').strip()
        with clients_lock:
            if not username or username in clients.values():
                proto.send_message(sock, 'ERRO', b'invalid username')
                return
            clients[sock] = username

        proto.send_message(sock, 'TEXT', f'* Вы присоединились, как {username}'.encode())
        broadcast('TEXT', f'{username} присоединился к чату', exclude=sock)
        print(f'{username} присоединился ({addr})')

        while True:
            msg = proto.recv_message(sock)
            if msg is None:
                print(f'[i] Пользователь {username} отключился без QUIT')
                break

            command, payload = msg
            if command == 'ADD':
                text = payload.decode('utf-8', errors='replace')
                if not text:
                    proto.send_message(sock, 'ERRO', b'Task text cannot be empty')
                    continue
                with tasks_lock:
                    tasks[text] = '[ ]'
                proto.send_message(sock, 'ADD', 'Задача добавлена'.encode())
            elif command == 'DONE':
                text = payload.decode('utf-8', errors='replace').strip()
                if not text.isdigit():
                    proto.send_message(sock, 'ERRO', b'Task number out of range')
                    continue
                idx = int(text) - 1
                with tasks_lock:
                    tasks_keys = list(tasks.keys())
                    if idx < 0 or idx >= len(tasks_keys):
                        proto.send_message(sock, 'ERRO', b'Task number out of range')
                        continue
                    tasks[tasks_keys[idx]] = '[x]'
                proto.send_message(sock, 'DONE', f'Задача {text} отмечена выполненной'.encode())
            elif command == 'LIST':
                with tasks_lock:
                    if not tasks:
                        res = 'Список задач пуст'
                    else:
                        a = []
                        for i, (task, status) in enumerate(tasks.items(), start=1):
                            a.append(f'{i}. {status} {task}')
                        res = '\n'.join(a)
                proto.send_message(sock, 'LIST', res.encode())
            elif command == "QUIT":
                proto.send_message(sock, "TEXT", b"* bye")
                print(f"[-] {username} вышел через QUIT")
                break
            else:
                proto.send_message(sock, "ERRO", f"unknown command {command}".encode())

    except ConnectionResetError:
        print(f"[!] {username or addr} - соединение сброшено (RST)")
    except BrokenPipeError:
        print(f"[!] {username or addr} - не удалось отправить, соединение разорвано")
    finally:
        with clients_lock:
            clients.pop(sock, None)
        sock.close()
        if username:
            broadcast("TEXT", f"* {username} покинул чат")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()
        print(f'[*] сервер слушает {HOST}:{PORT}')
        while True:
            client_socket, addr = server.accept()
            threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n[*] сервер остановлен')
