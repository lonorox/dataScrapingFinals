import json
import random

def generate_header():
    with open("config.json", "r") as f:
        config = json.load(f)
    user_agents = config['userAgents']
    proxies = config['proxies']
    user_agent = random.choice(user_agents)
    proxy = random.choice(proxies)
    return [user_agent, proxy]

def generate_tasks():
    # get tasks from json
    with open("config.json", "r") as f:
        config = json.load(f)

    return config["tasks"]