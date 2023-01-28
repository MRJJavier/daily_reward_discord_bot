
# This example requires the 'message_content' intent.
import os
from dotenv.main import load_dotenv
import discord
from discord.ext import tasks, commands



intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents=intents,command_prefix=commands.when_mentioned_or('/'))


def main():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(intents=intents,command_prefix=commands.when_mentioned_or("/"))
    
    load_dotenv()
    
    @bot.event
    async def on_ready():
        print(f"{bot.user.name} has connected to Discord.")
    
        for folder in os.listdir("modules"):
            if os.path.exists(os.path.join("modules",folder,"cog.py")):
                await bot.load_extension(f"modules.{folder}.cog")
    
    
    bot.run(os.getenv('DISCORD_TOKEN'))

if __name__ == '__main__':
    main()
