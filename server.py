import json
import socket
import threading


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = {} 
        self.log_file = "counter_log.txt"
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
                self.log_counter_update(client_id, 0)
                client_socket.sendall(response.encode('utf-8'))
                while self.server_socket.fileno() != -1:
                    print("Portal is opening...  87")
                    action_data = client_socket.recv(1024).decode('utf-8')
                    if not action_data:
                        break
                    action = json.loads(action_data)
        
                    if action.get("action") == "INCREASE":
                        self.log_counter_update(client_id, action.get("amount", 0))
                    else:
                        self.log_counter_update(client_id, -1*action.get("amount", 0))
            else:
                response = "Error: Client already registered"
                client_socket.sendall(response.encode('utf-8'))

        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()
    def log_counter_update(self, client_id, amount):
        try:
            current_value = self.clients[client_id]["counter"]
            new_value = current_value + amount
            with open(self.log_file, 'a') as log:
                log.write(f"Client {client_id}: Counter changed from {current_value} to {new_value}\n")
            self.clients[client_id]["counter"] = new_value

        except KeyError:
            print(f"Error: Client {client_id} not found.")

    def register_client(self, client_id, password):
        self.clients[client_id] = {"password": password, "counter": 0}
        return True


if __name__ == "__main__":
    server_instance = Server('127.0.0.1', 12345)
    server_instance.start_server()
