import struct


MAX_MESSAGE_SIZE = 10 * 1024 * 1024

def recv_exact(sock, size):
    data = b""
    while len(data) < size:
        b_l = size - len(data)
        chunk = sock.recv(b_l)
        if not chunk:
            raise Exception("Соединение пропало")
        data += chunk
    return data

def send_message(sock, command: str, payload: bytes):
    bytes_command = command.ljust(4).encode("utf-8")
    len_payload = len(payload)
    len_bytes = struct.pack("!I", len_payload)
    head = bytes_command + len_bytes + payload
    sock.sendall(head)

def recv_message(sock):
    a = recv_exact(sock, 8)
    command = a[:4].decode("utf-8").strip()
    payload_len = struct.unpack("!I", a[4:8])[0]
    if payload_len > MAX_MESSAGE_SIZE:
        raise ValueError("Размер сообщение превышает лимит")
    payload = recv_exact(sock, payload_len)
    return command, payload
