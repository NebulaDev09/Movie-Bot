import discord
from discord.ext import commands
import csv
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import json

load_dotenv()
TOKEN = os.getenv("TOKEN")
uri = os.getenv("uri")

client = MongoClient(uri)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

# class Create(discord.ui.LayoutView):    
#     text_display1 = discord.ui.TextDisplay(content="New movie night scheduled")
    
#     container1 = discord.ui.Container(
#         discord.ui.TextDisplay(content=f"ID: {ID}"),
#         discord.ui.TextDisplay(content=f"Name: {name}"),
#         discord.ui.TextDisplay(content=f"Genre: {genre}"),
#         discord.ui.TextDisplay(content=f"Date: {date}"),
#         discord.ui.TextDisplay(content=f"Time: {time}"),
#     )


class CreateModal(discord.ui.Modal, title="Enter Your recommendations"):

    field1 = discord.ui.TextInput(
        label="Name",
        placeholder="Type something...",
        required=True
    )

    field2 = discord.ui.TextInput(
        label="Genre",
        placeholder="Type something...",
        required=False
    )

    field3 = discord.ui.TextInput(
        label="Date",
        placeholder="Type something...",
        required=True
    )

    field4 = discord.ui.TextInput(
        label="Time",
        placeholder="Type something...",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            database = client.get_database("movienights")
            nights = database.get_collection("nights")
            ID = nights.count_documents({}) + 1
            name = self.field1.value.strip()
            date = self.field3.value.strip()
            time = self.field4.value.strip()
            if self.field2.value.strip() == "":
                genre = "NA"
            else:
                genre = self.field2.value.strip()
            night = {
                "ID": ID,
                "Name": name,
                "Genre": genre,
                "Date": date,
                "Time": time,
                "username": interaction.user.name,
                "userID": interaction.user.id,
            }
            nights.insert_one(night)
            await interaction.response.send_message(f"""Your movie night has been created,
ID: {ID}, 
Name: {name}, 
Genre: {genre}, 
Date: {date}, 
Time: {time}
by {interaction.user.name}""")
        except Exception as e:
            await interaction.response.send_message(f"An error occurred while submitting your recommendations: {e}", ephemeral=True)

# class MyModal(discord.ui.Modal, title="Enter Your reccomendations"):

#     field1 = discord.ui.TextInput(
#         label="First reccommendation",
#         placeholder="Type something...",
#         required=True
#     )

#     field2 = discord.ui.TextInput(
#         label="Second reccommendation",
#         placeholder="Type something...",
#         required=True
#     )

#     field3 = discord.ui.TextInput(
#         label="Third reccomendation",
#         placeholder="Type something...",
#         required=True
#     )

#     async def on_submit(self, interaction: discord.Interaction):
#         with open(CSV_FILE, mode="r+", newline="", encoding="utf-8") as f:
#             for row in csv.reader(f):
#                 if str(interaction.user.id) == row[0]:
#                     await interaction.response.send_message(
#                         "You have already submitted your recommendations.",
#                         ephemeral=True
#                     )
#                     return
#             if len([self.field1.value.strip().lower(), self.field2.value.strip().lower(), self.field3.value.strip().lower()]) != len({self.field1.value.strip().lower(), self.field2.value.strip().lower(), self.field3.value.strip().lower()}):
#                 await interaction.response.send_message(
#                     "You cannot submit the same recommendation multiple times.",
#                     ephemeral=True
#                 )
#                 return
#             else:
#                 writer = csv.writer(f)
#                 f.seek(0, os.SEEK_END)
#                 writer.writerow([
#                     interaction.user.id,
#                     str(interaction.user),
#                     self.field1.value.strip().lower(),
#                     self.field2.value.strip().lower(),
#                     self.field3.value.strip().lower()
#                 ])

#                 print([
#                     interaction.user.id,
#                     str(interaction.user),
#                     self.field1.value.strip().lower(),
#                     self.field2.value.strip().lower(),
#                     self.field3.value.strip().lower()
#                 ])

#                 await interaction.response.send_message(
#                     "Your response has been saved!",
#                     ephemeral=True
#                 )

# @bot.tree.command(name="recommend")
# async def recommend(interaction: discord.Interaction):
#     await interaction.response.send_modal(MyModal())

@bot.tree.command(name="ping")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!", ephemeral=True)

@bot.tree.command(name="make")
async def make(interaction: discord.Interaction):
    await interaction.response.send_modal(CreateModal())

@bot.tree.command(name="join")
async def join(interaction: discord.Interaction):
    pass

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")


bot.run(TOKEN)