import discord
from discord.ext import commands
import csv
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

CSV_FILE = "recommendations.csv"

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["User ID", "Username", "1", "2", "3"])


class MyModal(discord.ui.Modal, title="Enter Your reccomendations"):

    field1 = discord.ui.TextInput(
        label="First reccommendation",
        placeholder="Type something...",
        required=True
    )

    field2 = discord.ui.TextInput(
        label="Second reccommendation",
        placeholder="Type something...",
        required=True
    )

    field3 = discord.ui.TextInput(
        label="Third reccomendation",
        placeholder="Type something...",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        with open(CSV_FILE, mode="r+", newline="", encoding="utf-8") as f:
            for row in csv.reader(f):
                if str(interaction.user.id) == row[0]:
                    await interaction.response.send_message(
                        "You have already submitted your recommendations.",
                        ephemeral=True
                    )
                    return
            if len([self.field1.value.strip().lower(), self.field2.value.strip().lower(), self.field3.value.strip().lower()]) != len({self.field1.value.strip().lower(), self.field2.value.strip().lower(), self.field3.value.strip().lower()}):
                await interaction.response.send_message(
                    "You cannot submit the same recommendation multiple times.",
                    ephemeral=True
                )
                return
            else:
                writer = csv.writer(f)
                f.seek(0, os.SEEK_END)
                writer.writerow([
                    interaction.user.id,
                    str(interaction.user),
                    self.field1.value.strip().lower(),
                    self.field2.value.strip().lower(),
                    self.field3.value.strip().lower()
                ])

                print([
                    interaction.user.id,
                    str(interaction.user),
                    self.field1.value.strip().lower(),
                    self.field2.value.strip().lower(),
                    self.field3.value.strip().lower()
                ])

                await interaction.response.send_message(
                    "Your response has been saved!",
                    ephemeral=True
                )

@bot.tree.command(name="recommend")
async def recommend(interaction: discord.Interaction):
    await interaction.response.send_modal(MyModal())

@bot.tree.command(name="ping")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!", ephemeral=True)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")


bot.run(TOKEN)