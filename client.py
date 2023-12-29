import json
import socket
import time
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding



class User:
    @classmethod
    def read_config(cls, file_path):
        with open(file_path, 'r') as file:
            config_data = json.load(file)
        return config_data

    def __init__(self, server_ip, server_port):
        # Read config data
        config_data = self.read_config("userInfos/config.json")
        self.server_ip = server_ip
        self.server_port = server_port
        self.actions = config_data["actions"]["steps"]
        self.delay = float(config_data["actions"]["delay"])

        # Prompt the user for ID and password
        self.user_id_input = input("Enter your user ID: ")
        self.password_input = input("Enter your password: ")

    def increase(self, amount):
        print(f"User {self.user_id_input}: Increased counter by {amount}")

    def decrease(self, amount):
        print(f"User {self.user_id_input}: Decreased counter by {amount}")

    def generateKeys(self):
        # Generate an RSA Key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=3072,
            backend=default_backend()
        )

        # Get the Public Key from the Private Key
        public_key = private_key.public_key()
        self.public_key = public_key
        self.private_key = private_key

    def encrypt(message, public_key):
        # Message to be encrypted
        message = message.encode('utf-8')

        # Encrypting the message
        encrypted = public_key.encrypt(
            message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return encrypted

    def decrypt(encrypted, private_key):
        # Decrypting the message
        original_message = private_key.decrypt(
            encrypted,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        # Decode from bytes to string
        decoded_message = original_message.decode('utf-8')
        return decoded_message

    def connect_to_server(self):
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect((self.server_ip, self.server_port))

            # Send login credentials to the server
            login_data = {
                "id": self.user_id_input,
                "password": self.password_input
            }
            server_socket.sendall(json.dumps(login_data).encode('utf-8'))

            response = server_socket.recv(1024).decode('utf-8')

            # If the server sends a lock message, terminate the client
            if "Too many consecutive failed login attempts" in response:
                print(response)
                return
            # Check if login is successful
            if "successful" in response.lower():
                print(response)

                # Perform actions after successful login
                for action in self.actions:
                    time.sleep(self.delay)

                    if "INCREASE" in action.get("action", ""):
                        amount = action.get("amount", 1)
                        self.increase(amount)
                    elif "DECREASE" in action.get("action", ""):
                        amount = action.get("amount", 1)
                        self.decrease(amount)
                    else:
                        print(f"Unknown action: {action}")

                    action_data = json.dumps(action)
                    server_socket.sendall(action_data.encode('utf-8'))
                    print(f"Sent action to server: {action}")

            else:
                print("Login failed. Please check your credentials.")
                print(f"Wrong attempts: {response.split()[-1]}")

        except Exception as e:
            print(f"Error in connect_to_server: {e}")
        finally:
            server_socket.close()


if __name__ == "__main__":
    server_ip = input("Enter server IP: ")
    server_port = int(input("Enter server port: "))

    user_instance = User(server_ip, server_port)
    user_instance.connect_to_server()