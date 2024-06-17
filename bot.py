# This example requires the 'message_content' intent.
import discord
from discord.ext import commands
from discord.utils import get

from config import BOT_TOKEN
# from aioDB ..

# TODO: Make more verbose
description = "Bot for tracking LCM"

intents = discord.Intents.default()
intents.members = True # NOTE: (For personalized DMS)
intents.message_content = True

# client = discord.Client(intents=intents)

bot = commands.Bot(command_prefix='?', description=description, intents = intents)


# @bot.command(description='For when you wanna settle the score some other way')
# async def choose(ctx, *choices: str):
#     """Chooses between multiple choices."""
#     await ctx.send(random.choice(choices))
#

# # [Helper Functions]
def printContext(ctx):
    print( 
    f"""
    MSG:     {ctx.message.content}
    Author:  {ctx.author}
    Channel: {ctx.channel}
    Guild:   {ctx.guild}
    """
    )

#TODO:
def checkAddParamFormat():
    pass

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.startswith('$hello'):
        await message.channel.send('Hello! Use ?help for assistance!')
    await bot.process_commands(message)


# Message User "Reminder! Today you have to complete _____ problem(s)"
# @bot.event
# async def 

# [Commands] 
# TODO: Link discord commands to 'aioDB'

# ?help
@bot.command()
async def helpLCM(ctx):
    await ctx.send(
        '''
 Commands:
 ?addQuestion    -> Add Question
    > @param (str str str str)
    > ID (Integer)
    > Name
    > Difficulty ('E'/'M'/'H')
    > Question Type (Arr, LL, Stack, Queue, Tree, Hashing, BT, Graphs, Tries, Heaps, ..)
 ?updateQuestion -> Updae Question
 ?deleteQuestion -> Delete Question
 ?All            -> Display Question Bank
 ?History QID    -> Display Question, QID's, Submission History
        '''
    )

# ?add
@bot.command()
async def cmd_AddQuestion(ctx, *questionData: str):
    pass

# ?UpdateQuestion
async def cmd_UpdateQuestion(ctx):
    pass

# ?DeleteQuestion
async def cmd_DeleteQuestion(ctx):
    pass

# ?GetUpcoming
async def cmd_GetUpcoming(ctx):
    pass

# ?Todo
async def cmd_Todo():
    pass

# ?All
async def DisplayDB(ctx):
    pass

bot.run(BOT_TOKEN)
