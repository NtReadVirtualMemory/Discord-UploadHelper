import discord
from discord.ext import commands
import requests
from io import BytesIO
import time
import os
from keep_alive import keep_alive

# Bot setup
intents = discord.Intents.default()
intents.messages = True 
intents.guilds = True  
intents.message_content = True 
intents.voice_states = True 

bot = commands.Bot(command_prefix="!", intents=intents)

# Configure IDs
ROLE_ID = os.environ.get("PermissionRoleId") 


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith("!upload"):
        # Check for role only in guilds
        if message.guild:
            role = discord.utils.get(message.author.roles, id=ROLE_ID)
            if role:
                if message.attachments:
                    attachment = message.attachments[0]
                    file_url = attachment.url 
                    file_name = attachment.filename 

                    servers = requests.get("https://api.gofile.io/servers")
                    if servers.status_code == 200:
                        servers_data = servers.json()
                        servername = servers_data["data"]["servers"][0]["name"]

                        file_data = requests.get(file_url).content
                        upload_url = f"https://{servername}.gofile.io/uploadFile"
                        files = {'file': (file_name, file_data)}

                        attempts = 0
                        success = False
                        while attempts < 3 and not success:
                            response = requests.post(upload_url, files=files)
                            attempts += 1
                            if response.status_code == 200:
                                upload_data = response.json()
                                if upload_data["status"] == "ok":
                                    link = upload_data["data"]["downloadPage"]
                                    await message.channel.send(f"File Uploaded!\n{link}")
                                    success = True
                                    return
                                else:
                                    await message.channel.send(f"Error uploading file (Attempt {attempts}/3).")
                                    return
                            else:
                                await message.channel.send(f"Error connecting to GoFile (Attempt {attempts}/3).")
                                time.sleep(2)

                        if not success:
                            await message.channel.send("Upload failed after 3 attempts.")
                            return
                    else:
                        await message.channel.send("Error fetching server data.")
                        return
                else:
                    await message.channel.send("No file found to upload.")
                    return
            else:
                await message.channel.send("You do not have permission to use this command.")
                return
        else:
            # DM Handler
            if message.attachments:
                attachment = message.attachments[0]
                file_url = attachment.url 
                file_name = attachment.filename 

                servers = requests.get("https://api.gofile.io/servers")
                if servers.status_code == 200:
                    servers_data = servers.json()
                    servername = servers_data["data"]["servers"][0]["name"]

                    file_data = requests.get(file_url).content
                    upload_url = f"https://{servername}.gofile.io/uploadFile"
                    files = {'file': (file_name, file_data)}

                    attempts = 0
                    success = False
                    while attempts < 3 and not success:
                        response = requests.post(upload_url, files=files)
                        attempts += 1
                        if response.status_code == 200:
                            upload_data = response.json()
                            if upload_data["status"] == "ok":
                                link = upload_data["data"]["downloadPage"]
                                await message.channel.send(f"File Uploaded!\n{link}")
                                success = True
                                return
                            else:
                                await message.channel.send(f"Error uploading file (Attempt {attempts}/3).")
                                return
                        else:
                            await message.channel.send(f"Error connecting to GoFile (Attempt {attempts}/3).")
                            time.sleep(2)

                    if not success:
                        await message.channel.send("Upload failed after 3 attempts.")
                        return
                else:
                    await message.channel.send("Error fetching server data.")
                    return
            else:
                await message.channel.send("No file found to upload.")
                return

    await bot.process_commands(message)


TOKEN = os.environ.get("TOKEN")

keep_alive()
bot.run(TOKEN)
