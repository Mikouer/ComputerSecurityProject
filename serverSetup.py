import json
import secrets
import socket


def read_config(file_path):
    with open(file_path, 'r') as file:
        config_data = json.load(file)
    return config_data


class Client:

    def __init__(self):
        pass

    def init_count(self):
        # initialize the count
        pass


class User:
    def __init__(self, user_id, password, server_ip, port):
        self.id = user_id
        self.password = password
        self.server_ip = server_ip or "default_ip"
        self.port = port or "default_port"


    def increase(self):
        # TODO: implement increase action
        pass

    def decrease(self):
        # TODO: implement decrease action
        pass

    def connect_to_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((self.server_ip, int(self.port)))

        # Send registration data to the server
        registration_data = {
            "id": self.id,
            "password": self.password
        }
        server_socket.sendall(json.dumps(registration_data).encode('utf-8'))

        # Receive and print the server's response
        response = server_socket.recv(1024).decode('utf-8')
        print(response)

        # TODO: Implement further actions and communication with the server

        # Close the socket after registration
        server_socket.close()

# an example method for generating random id, password.
def generate_credentials():
    # Generate unique ID and password using secrets module
    user_id = secrets.token_hex(8)
    password = secrets.token_hex(12)
    return user_id, password


def registration():
    # TODO: get ip and port (socket? idk)

    # Generate credentials
    user_id, password = generate_credentials()

    # TODO: handle errors during registration

    return user_id, password


# Perform registration
user_credentials = registration()

if not user_credentials:
    print("There is an error during registration")
else:
    print("Your id is " + user_credentials[0])
    print("Your password is " + user_credentials[1])

# Read config file
config_data = read_config('userInfos/config.json')

# Create a User instance
user_instance = User(*user_credentials, config_data.get("server_ip", "default_ip"),
                     config_data.get("port", "default_port"))


# ---------------------------------------ServerClass:----------------

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
