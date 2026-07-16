import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
TOKEN = os.getenv("TOKEN")
uri = os.getenv("uri")

client = MongoClient(uri)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)


def score_movies(ID):
    try:
        database = client.get_database("movienights")
        nights = database.get_collection("nights")
        night = nights.find_one({"ID": ID})
        reccommendations = night["recommendations"]
        movies = {}
        for i in reccommendations.values():
            for j in i:
                if j in movies:
                    movies[j] += 1
                else:
                    movies[j] = 1
        return movies
    except Exception as e:
        print(f"An error occurred while calculating scores: {e}")

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
                "users": [interaction.user.id],
                "recommendations": {},
                "active": True
            }
            nights.insert_one(night)

            embed = discord.Embed(title="Movie night created", description=f"ID: {ID}")
            embed.add_field(name="Name", value=name, inline=False)
            embed.add_field(name="Genre", value=genre, inline=False)
            embed.add_field(name="Date", value=date, inline=False)
            embed.add_field(name="Time", value=time, inline=False)
            embed.add_field(name="Created by", value=f"<@{interaction.user.id}>", inline=False)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred while submitting your recommendations: {e}", ephemeral=True)

class RecommendModal(discord.ui.Modal, title="Enter Your recommendations"):

    def __init__(self, id: int):
        super().__init__()
        self.id = id

    field1 = discord.ui.TextInput(
        label="First recommendation",
        placeholder="Type something...",
        required=True
    )

    field2 = discord.ui.TextInput(
        label="Second recommendation",
        placeholder="Type something...",
        required=True
    )

    field3 = discord.ui.TextInput(
        label="Third recommendation",
        placeholder="Type something...",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        if len([self.field1.value.strip().lower(), self.field2.value.strip().lower(), self.field3.value.strip().lower()]) != len({self.field1.value.strip().lower(), self.field2.value.strip().lower(), self.field3.value.strip().lower()}):
            await interaction.response.send_message(
                "You cannot submit the same recommendation multiple times.",
                ephemeral=True
            )
            return
        else:
            try:
                database = client.get_database("movienights")
                nights = database.get_collection("nights")
                night = nights.find_one({"ID": self.id})
                reccommendations = night["recommendations"]
                reccommendations[str(interaction.user.id)] = [
                    self.field1.value.strip().lower(),
                    self.field2.value.strip().lower(),
                    self.field3.value.strip().lower()
                ]
                nights.update_one({"ID": self.id}, {"$set": {"recommendations": reccommendations}})
            except Exception as e:
                await interaction.response.send_message(f"An error occurred while submitting your recommendations: {e}", ephemeral=True)
           
            await interaction.response.send_message(
                "Your response has been saved!",
                ephemeral=True
            )

@bot.tree.command(name="recommend")
async def recommend(interaction: discord.Interaction, id: str):
    try:
        id = int(id)
        database = client.get_database("movienights")
        nights = database.get_collection("nights")
        night = nights.find_one({"ID": id})
        if night is None:
            await interaction.response.send_message("You have not created a movie night yet. Please create one first.", ephemeral=True)
            return
        elif interaction.user.id not in night["users"]:
            await interaction.response.send_message("You have not joined this movie night. Please join it first.", ephemeral=True)
            return
        elif interaction.user.id in night["recommendations"]:
            await interaction.response.send_message("You have already submitted your recommendations for this movie night.", ephemeral=True)
            return
        elif not night["active"]:
            await interaction.response.send_message(f"This movie night with ID: {id} is no longer accepting recommendations.", ephemeral=True)
            return
        else:
            await interaction.response.send_modal(RecommendModal(id))
    except Exception as e:
        await interaction.response.send_message(f"An error occurred while processing your request: {e}", ephemeral=True)

@bot.tree.command(name="ping")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!", ephemeral=True)

@bot.tree.command(name="make")
async def make(interaction: discord.Interaction):
    await interaction.response.send_modal(CreateModal())

@bot.tree.command(name="join")
async def join(interaction: discord.Interaction, id: str):
    try:
        id = int(id)
        database = client.get_database("movienights")
        nights = database.get_collection("nights")
        night = nights.find_one({"ID": id})
        if night is None:
            await interaction.response.send_message(f"No movie night scheduled with the ID: {id}", ephemeral=True)
        elif not night["active"]:
            await interaction.response.send_message(f"The movie night with ID: {id} is no longer taking recommendations.", ephemeral=True)
        else:
            if interaction.user.id in night["users"]:
                await interaction.response.send_message(f"You have already joined the movie night with ID: {id}", ephemeral=True)
            else:
                nights.update_one({"ID": id}, {"$push": {"users": interaction.user.id}})
                await interaction.response.send_message(f"You have successfully joined the movie night with ID: {id}", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)

@bot.tree.command(name="list")
async def list(interaction: discord.Interaction, id:str):
    id = int(id)
    try:
        database = client.get_database("movienights")
        nights = database.get_collection("nights")
        night = nights.find_one({"ID": id})
        if night is None:
            await interaction.response.send_message(f"No movie night scheduled with the ID: {id}", ephemeral=True)
        else:
            name = night["Name"]
            genre = night["Genre"]
            date = night["Date"]
            time = night["Time"]
            people = night["users"]
            embed = discord.Embed(title=f"Movie Night ID: {id}", description=f"Details of the movie night with ID: {id}")
            embed.add_field(name="Name", value=name, inline=False)
            embed.add_field(name="Genre", value=genre, inline=False)
            embed.add_field(name="Date", value=date, inline=False)
            embed.add_field(name="Time", value=time, inline=False)
            embed.add_field(name="People joined", value=', '.join(f'<@{person}>' for person in people), inline=False)
            reccommendations = night["recommendations"]
            if interaction.user.id == night["userID"]:
                message = "Here are the recommendations submitted by users:\n"
                for user, recs in reccommendations.items():
                    message += f"<@{user}>: {', '.join(recs)}\n"
                embed.add_field(name="Recommendations", value=message, inline=False)
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)

@bot.tree.command(name="end")
async def end(interaction: discord.Interaction, id:str):
    id = int(id)
    try:
        database = client.get_database("movienights")
        nights = database.get_collection("nights")
        night = nights.find_one({"ID": id})
        if night is None:
            await interaction.response.send_message(f"No movie night scheduled with the ID: {id}", ephemeral=True)
        elif interaction.user.id != night["userID"]:
            await interaction.response.send_message(f"You are not the creator of the movie night with ID: {id}. Only the creator can end it.", ephemeral=True)
        elif not night["active"]:
            await interaction.response.send_message(f"The movie night with ID: {id} has already ended.", ephemeral=True)
        else:
            nights.update_one({"ID": id}, {"$set": {"active": False}})
            people = night["users"]
            scores = score_movies(id)
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            embed = discord.Embed(title=f"{night['name']}, ID: {id} has ended", description="Here are the movie recommendations and their scores:")
            message = ""
            for movie, score in sorted_scores:
                message += f"- {movie}: {score}\n"
            embed.add_field(name="Recommendations", value=message, inline=False)
            embed.add_field(name="People joined", value=', '.join(f'<@{person}>' for person in people), inline=False)
            embed.add_field(name="Created by", value=f"<@{night['userID']}>", inline=False)
            embed.add_field(name="Date", value=night["Date"], inline=False)
            embed.add_field(name="Time", value=night["Time"], inline=False)
            embed.add_field(name="Genre", value=night["Genre"], inline=False)
            await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)

@bot.tree.command(name="help")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(title="Movie Night Bot Commands", description="Here are the available commands:")
    embed.add_field(name="/make", value="Create a new movie night.", inline=False)
    embed.add_field(name="/join <id>", value="Join an existing movie night with the given ID.", inline=False)
    embed.add_field(name="/recommend <id>", value="Submit your movie recommendations for the movie night with the given ID.", inline=False)
    embed.add_field(name="/list <id>", value="List the details of the movie night with the given ID.", inline=False)
    embed.add_field(name="/end <id>", value="End the movie night with the given ID and display the recommendations and scores. (Only the creator can end the movie night)", inline=False)
    embed.add_field(name="/help", value="Display this help message.", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")


bot.run(TOKEN)