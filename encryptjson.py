import json
import base64
from cryptography.fernet import Fernet

class ConfigManager:
    def __init__(self, key_path="encryption_key.key"):
        self.key_path = key_path
        self.load_or_create_key()

    def load_or_create_key(self):
        try:
            with open(self.key_path, 'rb') as key_file:
                self.key = key_file.read()
        except FileNotFoundError:
            self.key = Fernet.generate_key()
            with open(self.key_path, 'wb') as key_file:
                key_file.write(self.key)

    def encrypt(self, data):
        cipher = Fernet(self.key)
        encrypted_data = cipher.encrypt(data.encode('utf-8'))
        return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')

    def decrypt(self, encrypted_data):
        cipher = Fernet(self.key)
        decrypted_data = cipher.decrypt(base64.urlsafe_b64decode(encrypted_data))
        return decrypted_data.decode('utf-8')

    def encrypt_config(self, config):
        encrypted_config = config.copy()
        encrypted_config["id"] = self.encrypt(config["id"])
        encrypted_config["password"] = self.encrypt(config["password"])
        encrypted_config["server"]["ip"] = self.encrypt(config["server"]["ip"])
        encrypted_config["server"]["port"] = self.encrypt(str(config["server"]["port"]))
        return encrypted_config

    def decrypt_config(self, encrypted_config):
        decrypted_config = encrypted_config.copy()
        decrypted_config["id"] = self.decrypt(encrypted_config["id"])
        decrypted_config["password"] = self.decrypt(encrypted_config["password"])
        decrypted_config["server"]["ip"] = self.decrypt(encrypted_config["server"]["ip"])
        decrypted_config["server"]["port"] = int(self.decrypt(encrypted_config["server"]["port"]))
        return decrypted_config

if __name__ == "__main__":
    # Example usage:
    config_path = "userInfos/config.json"

    # Load the config
    with open(config_path, 'r') as file:
        config_data = json.load(file)

    # Encrypt the sensitive data
    config_manager = ConfigManager()
    encrypted_config = config_manager.encrypt_config(config_data)

    # Save the encrypted config to a new file
    encrypted_config_path = "encrypted_config.json"
    with open(encrypted_config_path, 'w') as file:
        json.dump(encrypted_config, file, indent=4)

    # Decrypt the config for use in the server
    decrypted_config = config_manager.decrypt_config(encrypted_config)
