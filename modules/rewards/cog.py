import asyncio
from datetime import datetime, timedelta
import re
from discord.ext import tasks,commands


class Rewards(commands.Cog, name="Rewards"):
    """Daily Rewards"""
    
    def __init__(self, bot: commands.Bot, rewards: dict, members: dict):
        self.bot = bot
        self.rewards = rewards
        self.members = members
        self.channel = 0
        self.index = 0
        self.rewardHour = 20
        self.printer.start()
        
    
    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(hours=1.0)
    async def printer(self):
        channel = self.bot.get_channel(self.channel)
        print(self.index)
        now = datetime.utcnow()
        offset = (self.rewardHour+12)%24
        if now.hour+1 >= offset:
            gmt = self.rewardHour-now.hour-1
        else:
            gmt = self.rewardHour-(24+now.hour+1)
            
        nextRewards= 'Next reward timezone is GMT'
        if gmt > 0: 
            nextRewards += f'+{gmt} \n'
        else: 
            nextRewards += f'{gmt} \n'
        
        
        try:
            if gmt in self.rewards:
                for m in self.rewards[gmt]:
                    nextRewards += f'{m} \n'
                await channel.send(f'{nextRewards}')
            await channel.send(f'{self.index}')
        except:
            print('set channel')
        self.index += 1
        
    @printer.before_loop
    async def prep(self):

        now = datetime.utcnow()
        future = datetime(now.year, now.month, now.day, (now.hour+1)%24, 1)

        if future < now: # if time is in the past
            future += timedelta(hours=1)  # delay to the next hour

        delta = (future - now).total_seconds()
        await asyncio.sleep(delta)


    
    
    @commands.command(description="Add a member to the reward list. /add @<Member> GMT+2")
    async def add(self, ctx, arg1, arg2):
        
        if arg1 in self.members:
           await self.remove(ctx,arg1)
    
        try:
            key = int(arg2.split("GMT")[1])
        except:
            await ctx.send("Try /add @<Member> GMT<-12,...,+12>")
            
        miembros = []
        if int(key) in self.rewards:
            miembros = self.rewards[key]
        miembros.append(arg1)
        self.rewards[key] = miembros
    
        self.members[arg1] = key
        await ctx.send(f'{arg1} has been added to {arg2} timezone')
    
    @commands.command(description="Remove a member from the reward list. /remove @<Member>")
    async def remove(self, ctx, arg1):
        
        miembros = self.rewards[self.members[arg1]]
        miembros.remove(arg1)
        if miembros == []:
            self.rewards.pop(self.members[arg1])
        else:
            self.rewards[self.members[arg1]] = miembros
        self.members.pop(arg1)
        await ctx.send(f'{arg1} has been removed')
        
        
    @commands.command(description="Set the reward hour (Default 20:00 UTC) /hour 20")
    async def hour(self, ctx, arg1):
        
        hora = int(arg1)
        
        if 0 <= hora and hora < 24:
            self.rewardHour = hora
        await ctx.send(f'The new reward hour is {hora}')
    
    @commands.command(description="Print reward list. /rewardlist")
    async def rewardlist(self, ctx):
        lista = ""
        s = sorted(self.rewards)
        for k in sorted(s):
            lista += '--------\n'
            if k < 0:
                lista += f'GMT{k}\n'
            else:
                lista += f'GMT+{k}\n'
            lista += '--------\n'
            for v in self.rewards[k]:
                lista += f'|-> {v} \n'
        
        await ctx.send(f'{lista}')
                
                
    @commands.command(description="Set the channel where the bot will write. /setchannel #<Channel>")
    async def setchannel(self, ctx,arg1):
        print(arg1)
        self.channel=int(re.split(r'\W+',str(arg1))[1])
        await ctx.send(f'{arg1}')
        

async def setup(bot: commands.Bot):
     # reward <K, List<V>>
    rewards = {}
    # members <V, K>
    members = {}
    await bot.add_cog(Rewards(bot,rewards,members))