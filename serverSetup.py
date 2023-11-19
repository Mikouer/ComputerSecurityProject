import json
import secrets


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
        self.server_ip = server_ip if 'server_ip' in server_ip else "default_ip"
        self.port = port if 'port' in port else "default_port"

    def increase(self):
        # TODO: implement increase action
        pass

    def decrease(self):
        # TODO: implement decrease action
        pass


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
