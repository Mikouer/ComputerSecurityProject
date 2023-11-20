import json
import socket
import threading


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = {}  # Store registered clients
        self.log_file = "counter_log.txt"  # Log file to record changes to counters

        # Create and bind the server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()

    def __del__(self):
        self.server_socket.close()

    def start_server(self):
        print(f"Server listening on {self.host}:{self.port}")
        try:
            while True:
                client_socket, client_address = self.server_socket.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                client_thread.start()

        except KeyboardInterrupt:
            print("Server terminated by user.")
        except Exception as e:
            print(f"Error in start_server: {e}")
        finally:
            self.server_socket.close()

    def handle_client(self, client_socket, client_address):
        try:
            config_data = client_socket.recv(1024).decode('utf-8')
            config = json.loads(config_data)

            client_id = config["id"]
            password = config["password"]
            self.clients[client_id] = {"password": password, "counter": 0}

            if self.register_client(client_id, password):
                response = f"Registration successful. Password set: {password}"
                self.log_counter_change(client_id, 0)  # Log initial counter value
                client_socket.sendall(response.encode('utf-8'))
                # TODO: Implement further actions and communication with the client
            else:
                response = "Error: Client already registered"
                client_socket.sendall(response.encode('utf-8'))

        except Exception as e:
            print(f"Error handling client: {e}")

        finally:
            client_socket.close()

    def log_counter_change(self, client_id
                           , new_value):
        # Log the change to the counter in the log file
        with open(self.log_file, 'a') as log:
            log.write(f"Client {client_id}: Counter changed to {new_value}\n")

    def register_client(self, client_id, password):
        self.clients[client_id] = {"password": password, "counter": 0}
        return True



if __name__ == "__main__":
    server_instance = Server('127.0.0.1', 12345)
    server_instance.start_server()
