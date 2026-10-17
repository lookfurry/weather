import discord
from discord import app_commands
from discord.ext import commands
import aiohttp

TOKEN = "token"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot {bot.user} is ready!")

@bot.tree.command(name="weather", description="Get the weather for any city")
@app_commands.describe(city="City name (e.g kiev)")
async def weather(interaction: discord.Interaction, city: str):
    await interaction.response.defer()
    
    async with aiohttp.ClientSession() as session:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        async with session.get(geo_url) as geo_resp:
            geo_data = await geo_resp.json()
            
            if not geo_data.get("results"):
                await interaction.followup.send(f"City **{city}** not found.")
                return
                
            location = geo_data["results"][0]
            lat = location["latitude"]
            lon = location["longitude"]
            city_name = location["name"]
            country = location.get("country", "")
            
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        async with session.get(weather_url) as weather_resp:
            weather_data = await weather_resp.json()
            temp = weather_data["current_weather"]["temperature"]
            
            if temp < 10:
                feeling = "Cold"
            elif 10 <= temp < 25:
                feeling = "Warm"
            else:
                feeling = "Hot"
                
            await interaction.followup.send(
                f"City: **{city_name}** ({country})\n"
                f"Temperature: **{temp}°C**\n"
                f"Condition: **{feeling}**"
            )

bot.run(TOKEN)
