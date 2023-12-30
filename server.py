import json
import socket
import threading
import ssl
import select
import base64
from cryptography.fernet import Fernet  # Make sure to install cryptography package

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = {}  # Store registered clients
        self.log_file = "counter_log.txt"  # Log file to record changes to counters
        self.server_socket = None
        self.failed_login_attempts = {}
        self.ssl_enabled = False
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        self.encryption_key = None
        self.cipher = None
        self.load_encryption_key()

    def initialize_server_socket(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if self.ssl_enabled:
            # wrap socket with SSL/TLS
            # note: we need a valid certificate (server_cert.pem) and private key (server_key.pem) files for the SSL/TLS configuration
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(certfile="server_cert.pem", keyfile="server_key.pem")
            self.server_socket = context.wrap_socket(self.server_socket, server_side=True)

        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()

    def __del__(self):
        if self.server_socket:
            self.server_socket.close()

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

    def start_server(self):
        self.initialize_server_socket()
        print(f"Server listening on ******:******")
        self.generateKeys()
        try:
            while True:
                # Use select to check for incoming data with a timeout
                ready_to_read, _, _ = select.select([self.server_socket], [], [], 30.0)

                if ready_to_read:
                    client_socket, client_address = self.server_socket.accept()
                    client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                    client_thread.start()
                else:
                    # No new message incoming for 30 seconds, close the server socket
                    print("No new messages for 30 seconds. Closing the server.")
                    break

        except KeyboardInterrupt:
            print("Server terminated by user.")
        except Exception as e:
            print(f"Error in start_server: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()

    def handle_client(self, client_socket, client_address):
        try:
            
            # client_public_key = client_socket.recv(1024)
            # client_socket.send(self.public_key)
            

            # testMessage = "test for encryption"
            # encrypted = self.encrypt(testMessage,client_public_key)
            # client_socket.send(encrypted)


            config_data = client_socket.recv(1024).decode('utf-8')
            config = json.loads(config_data)

            client_id = config["id"]
            password = config["password"]
            
            self.clients[client_id] = {"password": password, "counter": 0}

            if self.check_failed_login(client_id):
                attempts = self.failed_login_attempts[client_id]
                response = f"Error: Too many consecutive failed login attempts. Account locked. Attempts: {attempts}"
                client_socket.sendall(response.encode('utf-8'))
                return

            if self.check_credentials_match(client_id, password):
                response = f"Login successful for client {client_id}"
                client_socket.sendall(response.encode('utf-8'))
            else:
                self.log_failed_login(client_id)
                attempts = self.failed_login_attempts.get(client_id, 0)
                response = f"Error: Login failed. Please check your credentials. Attempts: {attempts}"
                print(response)
                client_socket.sendall(response.encode('utf-8'))

            # Continue with the rest of the logic only if the login is successful
            while self.server_socket.fileno() != -1:
                print("Portal is opening...  87")
                action_data = client_socket.recv(1024).decode('utf-8')
                if not action_data:
                    break
                action = json.loads(action_data)

                if action.get("action") == "INCREASE":
                    self.log_counter_update(client_id, action.get("amount", 0))
                else:
                    self.log_counter_update(client_id, -1 * action.get("amount", 0))

        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            # Check if the client socket is still open before trying to close it
            if client_socket.fileno() != -1:
                client_socket.close()

    def check_credentials_match(self, client_id, password):
        config_data = self.load_config()
        try:
            stored_id = config_data["id"]
            stored_password = config_data["password"]
            return client_id == stored_id and password == stored_password
        except KeyError:
            print(f"Error: Unable to validate credentials for client {client_id}")
            return False

    def load_counter_log(self):
        try:
            with open(self.log_file, 'r', encoding='utf-8') as log:
                # Read and decrypt the content from the log file
                log_content = log.read()
                decrypted_content = self.decrypt(log_content)
                print(decrypted_content)
        except FileNotFoundError:
            print(f"Log file {self.log_file} not found.")

    def load_encryption_key(self):
        try:
            with open("encryption_key.key", 'rb') as key_file:
                self.encryption_key = key_file.read()
                self.cipher = Fernet(self.encryption_key)
        except FileNotFoundError:
            print("Error: Encryption key file not found.")
            exit(1)

    def load_config(self):
        config_path = "userInfos/config.json"
        try:
            with open(config_path, 'r') as file:
                config_data = json.load(file)
                # Decrypt sensitive information
                config_data["id"] = self.decrypt(config_data["id"])
                config_data["password"] = self.decrypt(config_data["password"])
                config_data["server"]["ip"] = self.decrypt(config_data["server"]["ip"])
                config_data["server"]["port"] = int(self.decrypt(config_data["server"]["port"]))
                return config_data
        except (FileNotFoundError, KeyError):
            print(f"Error: Unable to read config file {config_path}")
            exit(1)
    def log_counter_update(self, client_id, amount):
        try:
            current_value = self.clients[client_id]["counter"]
            new_value = current_value + amount

            # Encrypt the client_id before writing to the log
            encrypted_client_id = self.encrypt(client_id)

            with open(self.log_file, 'a', encoding='utf-8') as log:
                log.write(f"Client {encrypted_client_id}: Counter changed from {current_value} to {new_value}\n")

            self.clients[client_id]["counter"] = new_value

        except KeyError:
            print(f"Error: Client {client_id} not found.")

    # These two method encrypt,decrypt, is for decrypting json file for method <load_config> , and encrypting id for methond<log_counter_update>
    # These two method is not relevant to the communication message encryption & decryption.
    def encrypt(self, data):
        # Use Fernet symmetric encryption for simplicity
        encrypted_data = self.cipher.encrypt(data.encode('utf-8'))
        return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')

    def decrypt(self, encrypted_data):
        decrypted_data = self.cipher.decrypt(base64.urlsafe_b64decode(encrypted_data))
        return decrypted_data.decode('utf-8')

    def check_failed_login(self, client_id):
        max_failed_attempts = 3
        if client_id in self.failed_login_attempts:
            self.failed_login_attempts[client_id] += 1
            if self.failed_login_attempts[client_id] >= max_failed_attempts:
                print(f"Account for client {client_id} locked. Too many consecutive failed login attempts.")
                return True
        else:
            self.failed_login_attempts[client_id] = 0
        return False

    def log_failed_login(self, client_id):
        if client_id in self.failed_login_attempts:
            self.failed_login_attempts[client_id] += 1
        else:
            self.failed_login_attempts[client_id] = 0

    def register_client(self, client_id, password):
        self.clients[client_id] = {"password": password, "counter": 0}
        if client_id in self.failed_login_attempts:
            del self.failed_login_attempts[client_id]

        return True

    def enable_ssl(self):
        self.ssl_enabled = True
        # Re-initialize the server socket with SSL/TLS
        self.initialize_server_socket()


if __name__ == "__main__":
    server_instance = Server('127.0.0.1', 12345)
   # server_instance.enable_ssl()  # Enable SSL/TLS
    server_instance.start_server()
