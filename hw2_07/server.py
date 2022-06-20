import socket


def server_func(host, port):
    with socket.socket() as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        print(f'{host}:{port} is waiting for a client connection...')
        s.listen(1)
        connect, addr = s.accept()
        print(f"Connected by {addr}")
        with connect:
            while True:
                try:
                    data = connect.recv(1024)
                    print(f'{data.decode()}')
                    connect.send(
                        f'The message has been successfully delivered to {host}:{port}.'.encode())
                except:
                    print(
                        f'The connection with {addr} is lost. Waiting for other client connection...')
                    connect, addr = s.accept()
                    print(f"Connected by {addr}")
