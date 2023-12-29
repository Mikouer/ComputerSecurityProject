import json
import secrets
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

    def __init__(self, config_file="user_config.json"):
        config_data = self.read_config(config_file)
        self.id = config_data["id"]
        self.password = config_data["password"]
        self.server_ip = config_data["server"]["ip"]
        self.server_port = int(config_data["server"]["port"])
        self.actions = config_data["actions"]["steps"]
        self.delay = float(config_data["actions"]["delay"])
        

    def increase(self, amount):
        print(f"User {self.id}: Increased counter by {amount}")

    def decrease(self, amount):
        print(f"User {self.id}: Decreased counter by {amount}")

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
        
    def encrypt(message,public_key):
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

    def decrypt(encrypted,private_key):
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

            registration_data = {
                "id": self.id,
                "password": self.password
            }
            server_socket.sendall(json.dumps(registration_data).encode('utf-8'))

            response = server_socket.recv(1024).decode('utf-8')
            print(response)


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
        # for debugging:
        #        response = server_socket.recv(1024).decode('utf-8')
        #        print(response)
            server_socket.close()

            # Close the socket after performing actions
        #   server_socket.close()

        except Exception as e:
            print(f"Error in connect_to_server: {e}")


if __name__ == "__main__":
    user_instance = User("userInfos/config.json")
    user_instance.connect_to_server()
