import random
import time
import json

def help_response(message: str):
    p_message = message
    welcome = '\tWelcome to the bot\n-----------------------------\n'
    h_message = f"{welcome}Type $hello to start chatting\n$talk to have a conversation\n$check to make sure bot is working\n$roll to roll from 1-10\n$list to see list of commands <-(This one)\n$dm to private message\n$code for code output\n$gif to get a random GIF\n$caption to add a caption to a prexisting GIF(caption | link)\n$art for an AI-generated art piece\n$help for more information"
    if (p_message == '$list'):
        return h_message

def sayHi(message: str):
    if (message == '$hello'):
        return 'Whats up'

def roll_response(message: str):
    p_message = message
    if (p_message == '$roll'):
        return random.choice(["Rolling the dice...", "Let's see what the dice says...", "Time to roll the dice!"])

def check_response(message: str):
    p_message = message
    if (p_message == '$check'):
        happy = "(❁´◡`❁)"
        TIMER= int(time.time() + random.randint(1,5))
        if TIMER == 0:
            TIMER = 'Hooray༼ つ ◕_◕ ༽つ'
        check_message = random.choice(["Bot has passed the check", "Alright alright alright", "Thank you Kanye very cool", "Do people still buy DogeCoin?", f"I am alive and well{happy}", f"Here's a timer <t:{TIMER}:R>"])
        return check_message

def get_config() -> dict:
    import os
    # get config.json path
    config_dir = os.getcwd()
    config_name = 'config.json'
    config_path = os.path.join(config_dir, config_name)

    with open(config_path, 'r') as f:
        config = json.load(f)

    return config
