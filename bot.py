import openai
import nextcord
from nextcord.ext import commands
from nextcord import Interaction, SlashOption, ChannelType
from nextcord.abc import GuildChannel
import aiohttp
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageSequence
from revChatGPT.ChatGPT import Chatbot
import base64
import time
import random
import json
import requests
import responses


#Allow bot to talk in channels
intents = nextcord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="$", intents = intents)

#testingServerID = 1058677478291423292

#Accesses JSON file with keys
config = responses.get_config()


def run_discord_bot():
    #Token and API keys
    TOKEN = config['discord_token']
    openai.api_key = config['openAI_key']
    giphy_api_key = config['giphy_api_key']

    #Runs the AI art generator
    class Dropdown(nextcord.ui.Select):
        def __init__(self, message, images, user):
            self.message = message
            self.images = images
            self.user = user

            options = [
                nextcord.SelectOption(label="1"),
                nextcord.SelectOption(label="2"),
                nextcord.SelectOption(label="3"),
                nextcord.SelectOption(label="4"),
                nextcord.SelectOption(label="5"),
                nextcord.SelectOption(label="6"),
                nextcord.SelectOption(label="7"),
                nextcord.SelectOption(label="8"),
                nextcord.SelectOption(label="9"),
            ]

            super().__init__(
                placeholder="Choose the image you want to see!",
                min_values=1,
                max_values=1,
                options=options,
            )

        async def callback(self, interaction: nextcord.Interaction):
            if not int(self.user) == int(interaction.user.id):
                await interaction.response.send_message("You are not the author of this message!", ephemeral=True)
            selection = int(self.values[0])-1
            image = image = BytesIO(base64.decodebytes(self.images[selection].encode("utf-8")))
            return await self.message.edit(content="Content Generated by **craiyon.com", file=nextcord.File(image, "Ai_Image.png"), view=DropdownView(self.message, self.images, self.user))

    class DropdownView(nextcord.ui.View):
        def __init__(self, message, images, user):
            super().__init__()
            self.message = message
            self.images = images
            self.user = user
            self.add_item(Dropdown(self.message, self.images, self.user))
    
    #Prints the bot is wokring in the terminal
    @client.event
    async def on_ready():
        print(f'{client.user} is running!')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        username = str(message.author.name)
        user_message = str(message.content)
        channel = str(message.channel.name)

        print(f"{username} said '{user_message}' in {channel}")

    #Slash commands
    @client.slash_command('hello', description = "says hello to you")
    async def hello(interaction: Interaction):
        username = interaction.user.mention
        user_message = interaction.message
        message = responses.sayHi(user_message)

        hello_message = random.choice(["What's up", "console.log(Hello World)", "Yo", "Glad you're here", "Welcome back"])
        if message:
            await interaction.response.send_message(f'{message} {username}!')
        else:
            await interaction.response.send_message(f'{hello_message} {username}!')

    @client.slash_command('check', description = "checks if the bot is working and sends a random message")
    async def check(interaction: Interaction):
        msg = interaction.message
        message = responses.check_response(msg)

        happy = "(❁´◡`❁)"
        TIMER= int(time.time() + random.randint(1,5))
        if TIMER == 0:
            TIMER = 'Hooray༼ つ ◕_◕ ༽つ'
        
        check_message = random.choice(["Bot has passed the check", "Alright alright alright", "Thank you Kanye very cool", "Do people still buy DogeCoin?", f"I am alive and well{happy}", f"Here's a timer <t:{TIMER}:R>"])
        if message:
            await interaction.response.send_message(f'{message}!')
        else:
            await interaction.response.send_message(f'{check_message}')

    @client.slash_command('roll', description = "rolls a random number from 1 - 10")
    async def roll(interaction: Interaction):
        roll = str(random.randint(1,10))
        roll_message = interaction.message
        message = responses.roll_response(roll_message)

        happy = "╰(*°▽°*)╯"
        roll_message = random.choice(["Rolling the dice...", "Let's see what the dice says...", f"Time to roll the dice{happy}!"])
        if message:
            await interaction.response.send_message(f'{message} You rolled a {roll}!')
        else:
            await interaction.response.send_message(f'{roll_message} You rolled a {roll}')

    @client.slash_command('list', description = "lists out the commands ands describes what each of them do")
    async def list(interaction:Interaction):
        help_msg = interaction.message
        message = responses.help_response(help_msg)

        welcome = '\tWelcome to the bot\n-----------------------------\n'
        h_message = f"{welcome}Type $hello to start chatting\n$talk to have a conversation\n$check to make sure bot is working\n$roll to roll from 1-10\n$list to see list of commands <-(This one)\n$dm to private message\n$code for code output\n$gif to get a random GIF\n$caption to add a caption to a prexisting GIF(link | caption)\n$art for an AI-generated art piece\n$help for more information"
        if message:
            await interaction.response.send_message(f'`{message}`')
        else:
            await interaction.response.send_message(f'`{h_message}`')

    @client.slash_command('chat', description = "start a conversation with the bot")
    async def chat(interaction: Interaction, message: str):
        chatbot = Chatbot({
            "session_token": config['session_token']
            }, conversation_id= None, parent_id=None)

        loading_message = await interaction.channel.send("Generating response... please wait.")
        response = chatbot.ask(message, conversation_id= None, parent_id=None)
        response_message = response['message']
        response_message = response_message.replace('\\n', '\n').replace('\\\\', '\\')
        
        if len(response_message) < 1900:
            await loading_message.edit(content = f"`Powered By OpenAI **chat.openai.com`\n{interaction.user.mention} your response is done!\n{response_message}")
        else:
            await loading_message.edit("The response was too long to display")

    @client.slash_command('code', description = "ask the bot to write code")
    async def code(interaction: Interaction, message: str):
        chatbot = Chatbot({
            "session_token": config['session_token']
            }, conversation_id= None, parent_id=None)

        loading_message = await interaction.channel.send("Generating response... please wait.")
        response = chatbot.ask(message, conversation_id= None, parent_id=None)
        response_message = response['message']
        response_message = response_message.replace('\\n', '\n').replace('\\\\', '\\')
        
        if len(response_message) < 1900:
            await loading_message.edit(f"`Powered By OpenAI **chat.openai.com`\n{interaction.user.mention} your response is done!\n{response_message}")
        else:
            await loading_message.edit("The response was too long to display")

    @client.slash_command('dm', description = "get a private response from the bot")
    async def dm(interaction: Interaction, message: str):
        dm_channel = await interaction.user.create_dm()
        chatbot = Chatbot({
            "session_token": config['session_token']
            }, conversation_id= None, parent_id=None)

        loading_message = await dm_channel.send("Generating response... please wait.")
        response = chatbot.ask(message, conversation_id= None, parent_id=None)
        response_message = response['message']
        response_message = response_message.replace('\\n', '\n').replace('\\\\', '\\')

        if len(response_message) < 1900:
            await loading_message.edit(f"`Powered By OpenAI **chat.openai.com`\n{response_message}")
        else:
            await loading_message.edit("The response was too long to display")

    @client.slash_command('art', description = "generates 9 Ai images")
    async def art(interaction: Interaction, prompt: str):
        ETA = int(time.time() + 60)
        msg = await interaction.channel.send(f"Sit back, relax, this might take a while... ETA: <t:{ETA}:R>")
        print(f"{client.user} is generating photos!")
        async with aiohttp.request("POST", "https://backend.craiyon.com/generate", json={"prompt": prompt}) as resp:
            data = await resp.json()
            images = data['images']
            image = BytesIO(base64.decodebytes(images[0].encode("utf-8")))
            await interaction.channel.send(interaction.user.mention + " your pictures are ready!")
            return await msg.edit(content="Content Generated by **craiyon.com", file=nextcord.File(image, "Ai_Image.png"), view=DropdownView(msg, images, interaction.user.id))

    @client.slash_command('gif', description = "generates a random gif")
    async def gif(interaction: Interaction, message: str):
        #Get the search term from the message
        search_term = " ".join(message)
        #Make a request to the Giphy API
        r = requests.get(
            "https://api.giphy.com/v1/gifs/search",
            params={
                "api_key": giphy_api_key,
                "q": search_term,
                "limit": 1,
                "offset": random.randint(0, 100),
                "rating": "pg-13",
                "lang": "en"
                }
            )
        #Get the URL of the first GIF in the search results
        gif_url = r.json()["data"][0]["url"]
        #Send the GIF to the channel
        await interaction.channel.send("`Powered By GIPHY **giphy.com`")
        return await interaction.channel.send(gif_url)
    
    @client.slash_command('caption', description = "puts a caption on a gif")
    async def caption(interaction: nextcord.Interaction, gif_url: str, *, caption: str):
        # Download the gif from the url
        response = requests.get(gif_url)
        gif_bytes = BytesIO(response.content)
        # Open the gif using PIL
        with Image.open(gif_bytes) as im:
            # Create a new image the same size as the gif
            frames = [frame.copy() for frame in ImageSequence.Iterator(im)]
            for frame in frames:
                draw = ImageDraw.Draw(frame)
                # Select the font and size you want to use
                font = ImageFont.truetype("arial.ttf", 24)
                # Position and add the caption text to the image
                draw.text((10, 10),caption, (255, 255, 255), font=font)
        
            # Save the new gif with caption text in it
            gif_with_caption = BytesIO()
            im.save(gif_with_caption, save_all=True, append_images=frames)
            gif_with_caption.seek(0)
            # upload the gif with caption to the channel
            await interaction.channel.send(gif_with_caption, filename="animated_with_caption.gif")

    #Regular prefix commands
    @client.command()
    async def hello(ctx):
        username = ctx.message.author.mention
        user_message = ctx.message.content
        await ctx.send(f'{responses.sayHi(user_message)} {username}!')

    @client.command()
    async def check(ctx):
        message = ctx.message.content
        await ctx.send(f'{responses.check_response(message)}!')
    
    @client.command()
    async def roll(ctx):
        roll = str(random.randint(1,10))
        roll_message = ctx.message.content
        await ctx.send(f'{responses.roll_response(roll_message)} You rolled a {roll}!')

    @client.command()
    async def list(ctx):
        help_message = ctx.message.content
        await ctx.send(f'`{responses.help_response(help_message)}`')
    
    @client.command()
    async def chat(ctx):
        message = ctx.message.content
        chatbot = Chatbot({
            "session_token": config['session_token']
            }, conversation_id= None, parent_id=None)

        response = chatbot.ask(message, conversation_id= None, parent_id=None)
        response_message = response['message']
        response_message = response_message.replace('\\n', '\n').replace('\\\\', '\\')
        await ctx.send("`Powered By OpenAI **chat.openai.com`")
        await ctx.send(f"{response_message}")

    @client.command()
    async def dm(ctx):
        message = ctx.message.content
        chatbot = Chatbot({
            "session_token": config['session_token']
            }, conversation_id= None, parent_id=None)

        response = chatbot.ask(message, conversation_id= None, parent_id=None)
        response_message = response['message']
        response_message = response_message.replace('\\n', '\n').replace('\\\\', '\\')
        await ctx.author.send("`Powered By OpenAI **chat.openai.com`")
        await ctx.author.send(f"{response_message}")

    @client.command()
    async def code(ctx):
        message = ctx.message.content
        chatbot = Chatbot({
            "session_token": config['session_token']
            }, conversation_id= None, parent_id=None)

        response = chatbot.ask(message, conversation_id= None, parent_id=None)
        response_message = response['message']
        response_message = response_message.replace('\\n', '\n').replace('\\\\', '\\')
        await ctx.send("`Powered By OpenAI **chat.openai.com`")
        await ctx.send(f"{response_message}")

    @client.command()
    async def gif(ctx):
        #Get the search term from the message
            search_term = " ".join(ctx.message.content[1:])
            #Make a request to the Giphy API
            r = requests.get(
                "https://api.giphy.com/v1/gifs/search",
                params={
                    "api_key": giphy_api_key,
                    "q": search_term,
                    "limit": 1,
                    "offset": random.randint(0, 100),
                    "rating": "g",
                    "lang": "en"
                    }
                )
            #Get the URL of the first GIF in the search results
            gif_url = r.json()["data"][0]["url"]
            #Send the GIF to the channel
            await ctx.send("`Powered By GIPHY **giphy.com`")
            return await ctx.send(gif_url)

    @client.command()
    async def caption(ctx):
        #Get the search term from the message
            message_parts = ctx.message.content[len("/caption"):].strip().split("|")
            search_term = message_parts[0].strip()
            caption = message_parts[1].strip()
            #Make a request to the Giphy API
            r = requests.get(
                "https://api.giphy.com/v1/gifs/search",
                params={
                   "api_key": giphy_api_key,
                    "q": search_term,
                    "limit": 1,
                    "offset": 0,
                    "rating": "g",
                    "lang": "en" 
                }
            )
            #Check if the data array is empty
            if not r.json()["data"]:
                #If the data array is empty, send a message to the channel indicating that no GIFs were found
                await ctx.send("No GIFs were found for the given search term.")
            else:
                #Get the URL of the first GIF in the search results
                gif_url = r.json()["data"][0]["url"]
                #Make a request to the Giphy API to create a new GIF with text
                r = requests.post(
                    "https://api.giphy.com/v1/gifs/create",
                    data={
                        "api_key": giphy_api_key,
                        "source_image_url": gif_url,  #Set the source image URL to the GIF that we searched for
                        "caption": caption,  #Set the caption to the user's specified caption
                        "text_color": "#FFFFFF",  #Set the text color to white
                        "text_font": "verdana",  #Set the text font to Verdana
                        "text_size": "35",  #Set the text size to 35
                        "text_align": "center"  #Set the text alignment to center
                        }
                    )
                #Check for errors
                print(r.json())
                #Get the URL of the new GIF with text
                gif_url_with_text = r.json()["data"]["url"]
                #Send the GIF to the channel
                await ctx.send("`Powered By GIPHY **giphy.com`") 
                return await ctx.send(gif_url_with_text)

    @client.command()
    async def art(ctx: commands.Context, *, prompt: str):
        ETA = int(time.time() + 60)
        msg = await ctx.send(f"Sit back, relax, this might take a while... ETA: <t:{ETA}:R>")
        print(f"{client.user} is generating photos!")
        async with aiohttp.request("POST", "https://backend.craiyon.com/generate", json={"prompt": prompt}) as resp:
            data = await resp.json()
            images = data['images']
            image = BytesIO(base64.decodebytes(images[0].encode("utf-8")))
            await ctx.send(ctx.message.author.mention + " your pictures are ready!")
            return await msg.edit(content="`Content Generated by **craiyon.com`", file=nextcord.File(image, "Ai_Image.png"), view=DropdownView(msg, images, ctx.author.id))

    client.run(TOKEN)