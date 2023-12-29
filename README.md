# ComputerSecurityProject-group15
## Group memebers
+ i6226172 Zijian Dong
+ i6267501 Zhefan Cheng
+ i6288444 Cui qi
+ i6283477 Yasune Notermans

## So far we done

Now we're done with the build it part, where each client, as a participant in a simulated communication network, first sends a registration request to the server, and when the request goes through, the server sends the client a message that registration is complete, along with his ID and password. Then the server starts initialising the counters and executes the actions defined by the client. We have defined and tested the actions increase and decrease, and the logs of the actions are recorded in the project directory in a text file called counter_log.txt.

## how to run
you can run server.py first. then open a new terminal to run client.py(by "py server.py"). also you can adjust the json file ,then read update from log file.




json_message = {
    "id": "test123",
    "password": "PASSWORD123",
    "server": {
        "ip": "127.0.0.1",
        "port": 12345
    },
    "actions": {
        "delay": 1,
        "steps": [
            {"action": "INCREASE", "amount": 5},
            {"action": "DECREASE", "amount": 2},
            {"action": "DECREASE", "amount": 9},
            {"action": "INCREASE", "amount": 8}
        ]
    }
}