import struct


MAX_SIZE_MESSAGE = 1024 * 1024 * 10
HEADER_FORMAT = '!4sI'
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
COMMAND_SIZE = 4

def recv_exact(sock, size):
    chunks = bytearray()
    while len(chunks) < size:
        chunk = sock.recv(size - len(chunks))
        if not chunk:
            raise ConnectionError('Подключение разорванно')
        chunks.extend(chunk)
    return bytes(chunks)

def send_message(sock, command, payload = b''):
    if len(payload) > MAX_SIZE_MESSAGE:
        raise ValueError(f'payload слишком большой: {MAX_SIZE_MESSAGE} байт!')
    command_bytes = command.encode('ascii').ljust(COMMAND_SIZE)[:COMMAND_SIZE]
    header = struct.pack(HEADER_FORMAT, command_bytes, len(payload))
    sock.sendall(header + payload)

def recv_message(sock):
    try:
        header = recv_exact(sock, HEADER_SIZE)
    except ConnectionError:
        return None
    command_bytes, length = struct.unpack(HEADER_FORMAT, header)
    if length > MAX_SIZE_MESSAGE:
        raise ValueError(f'Заявленная длинна {length} превышает лимит!')
    command = command_bytes.decode('ascii').strip()
    payload = recv_exact(sock, length)
    return command, payload