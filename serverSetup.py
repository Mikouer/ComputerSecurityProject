import json

def read_config(file_path):
    with open(file_path, 'r') as file:
        config_data = json.load(file)
    return config_data

class client:
    def __init__(self):
        pass
    def init_count():
        #initialize the count
        pass

class user:
    def __init__(self, config):
        self.id = config["id"]
        self.password = config["password"]
        self.serverIp = config["server_ip"]
        self.port = config["port"]

    def increase():
        #TODO: implement increase action
        pass
    def decrease():
        #TODO: implement increase action
        pass

def registration():
    #TODO: get ip and port(socket? idk)

    #TODO: generate id
    #TODO: generate password
    id = 0
    password = 0
    return id,password
    #if there's an error, then return false only

back = registration

if(not back):
    print("Here is an error")
else:
    print("Your id is "+back[0])
    print("Your password is "+back[1])
    user = back



config_data = read_config('userInfos/config.json')
user = user(config_data)


