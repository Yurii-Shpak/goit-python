import socket


def client_func(host, port):
    with socket.socket() as s:
        try:
            s.connect((host, port))
            while True:
                data = input('>>>')
                if data == 'exit':
                    break
                s.sendall(data.encode())
                print(f'{s.recv(1024).decode()}')
        except ConnectionRefusedError:
            print(f'The server {host}:{port} is not accessible.')
