import json
import secrets
import socket


class User:
    @classmethod
    def read_config(cls, file_path):
        with open(file_path, 'r') as file:
            config_data = json.load(file)
        return config_data

    def __init__(self, user_id, password, server_ip="localhost", port=12345):
        self.id = user_id
        self.password = password
        self.server_ip = server_ip
        self.port = port

    def increase(self):
        # TODO: Implement increase action
        pass

    def decrease(self):
        # TODO: Implement decrease action
        pass

    def connect_to_server(self):
        try:
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

        except Exception as e:
            print(f"Error in connect_to_server: {e}")



def generate_credentials():
    user_id = secrets.token_hex(8)
    password = secrets.token_hex(12)
    return user_id, password

def registration():
    try:
        user_id, password = generate_credentials()
        user_instance = User(user_id, password)
        user_instance.connect_to_server()
        return user_id, password
    except Exception as e:
        print(f"Error during registration: {e}")
        return None


# Perform registration
user_id, password = registration()

if not user_id or not password:
    print("There is an error during registration")
else:
    print("Your id is " + user_id)
    print("Your password is " + password)

# Read config file
config_data = User.read_config('userInfos/config.json')

# Create a User instance
user_instance = User(user_id, password, config_data.get("server_ip"), config_data.get("port"))
