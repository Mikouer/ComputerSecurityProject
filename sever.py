import json
import socket
import threading

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}  # Store registered clients

    def start_server(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()

        print(f"Server listening on {self.host}:{self.port}")

        while True:
            client_socket, client_address = self.server_socket.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
            client_thread.start()

    def handle_client(self, client_socket, client_address):
        try:
            config_data = client_socket.recv(1024).decode('utf-8')
            config = json.loads(config_data)

            client_id = config["id"]
            password = config["password"]

            if self.register_client(client_id, password):
                response = "Registration successful"
                client_socket.sendall(response.encode('utf-8'))
                # TODO: Implement further actions and communication with the client
            else:
                response = "Error: Client already registered"
                client_socket.sendall(response.encode('utf-8'))

        except Exception as e:
            print(f"Error handling client: {e}")

        finally:
            client_socket.close()

    def register_client(self, client_id, password):
        if client_id not in self.clients:
            self.clients[client_id] = {"password": password, "counter": 0}
            return True
        else:
            return False

if __name__ == "__main__":
    server_instance = Server('127.0.0.1', 12345)
    server_instance.start_server()
