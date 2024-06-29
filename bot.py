# This example requires the 'message_content' intent.
import discord
import os
from discord.ext import commands
from discord.utils import get
import aioDB as ADB
from datetime import timedelta, datetime
from schema import RETRY_TIME_WINDOW, USER_ID
from config import BOT_TOKEN

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
    if message.content.startswith('$hello LCM'):
        await message.channel.send("Hello! Use '?help' for assistance!")
    await bot.process_commands(message)


# Message User "Reminder! Today you have to complete _____ problem(s)"
# @bot.event
# async def 

# [Commands] 
# TODO: Link discord commands to 'aioDB'

# -- [Helper Commands]
# TODO: fix formatiing
@bot.command()
async def helpLCM(ctx):
    """LCM Bot-Specific Commands"""
    await ctx.send(
'''
```
 ?addQuestion <ID>, <NAME>, <DIFFICULTY>, <TYPE>
    [ Add Question ]
    > ID         (INT)
    > Name       (STR)
    > Difficulty ('E'/'M'/'H')
    > Type       (use ?listTypes for options)
 ?addSubmission
    [ Add Question Submission. ]
 ?changeRetryWindow <DAY>
    [ Change duration bot waits until notifying user to retry a question (default = 2 days) ]
    > DAY        (INT)
 ?updateQuestion    -> [ Update Question ]
 ?deleteQuestion    -> [ Delete Question ]
 ?All               -> [ Display Question Bank ]
 ?history <QID>     -> [ Display Question, QID's, Submission History ]
 ?listTypes         -> [ Display Possible Question Types ]
 ?getUpcoming       -> [ Display Failed Questions to Reattempt]
 ?todo              -> [ Display Failed Question Scheduled to Reattempt Today]
```
'''
)

QUESTION_TYPES = ["ARR", "LL", "HASHING", "TWOPOINTER", "BINARYSEARCH", "SLIDINGWINDOW", "TREES", "TRIES", "BACKTRACKING", "BFS", "DFS", "RECURSION", "HEAPS", "GRAPHS", "GREEDY", "GRAPHS"]

#TODO: Clean up make nicer
def checkAddQuestionInputFormat(QID: str, NAME: str, DIFF: str, TYPE: str):
    if not QID or not NAME or not DIFF or not TYPE:
        print("Not all parameters exist")
        return False 
    elif not QID.isdigit():
        return False
    elif DIFF.upper() not in ["E", "M", "H"]:
        print("NOT E/M/H")
        return False
    elif TYPE.upper() not in QUESTION_TYPES:
        print("NOT A VALID TYPE")
        return False
    return True

#TODO: Clean up make nicer
def checkAddSubmissionInputFormat(QID, COMP, CODE, NOTES):
    if not QID:
        print("Not all parameters exist")
        return False 
    elif not QID.isdigit():
        print("QID Not digit")
        return False
    return True

# -- [INSERTION COMMANDS] --

#Add Character limitaion for NOTES and CODE
async def promptSub(ctx, QID):
    if not (await ADB.checkExisting("QuestionBank", "Question_ID", QID)):
        await ctx.send("Question ID does not exist. Please add it using ?addQuestion")
        return

    def check(m):
        return m.channel == ctx.channel and m.author == ctx.author
    await ctx.send("```Did you complete the Question? (T/F)```") 
    COMP = True if (await bot.wait_for('message', check=check)).content.upper() == "T" else False
    await ctx.send("```What code did you use? Enter 'x' to skip```") 
    CODE = ( await bot.wait_for('message', check=check) ).content
    await ctx.send("```Any Notes? Enter 'x' to skip```") 
    NOTES = ( await bot.wait_for('message', check=check) ).content

    if CODE.strip().lower() == "x":
        CODE = ""
    if NOTES.strip().lower() == "x":
        NOTES = ""

    retryWindow = await ADB.getRetryWindow(ctx.author.id)

    # x = 0
    # if retryWindow != None:
    #     x = datetime.today() + retryWindow
    # print(f"retryWindow {retryWindow} new retrydate {x}") 

    if not checkAddSubmissionInputFormat(QID, COMP, CODE, NOTES) or retryWindow == None:
        await ctx.send("Please try again!")
        return ()

    return (QID, COMP, CODE, datetime.today(), datetime.today() + retryWindow, NOTES, ctx.author.id)

@bot.command()
async def changeRetryWindow(ctx, day):
    """Update the duration LCM-bot waits until notifying User to retry failed question attempt. (Default duration = 2 days)"""
    if day.isdigit():
    #   convertedVal = int(RETRY_TIME_WINDOW.total_seconds())
        d = int(day)
        await ADB.updateRetryDate(ctx.author.id, int(timedelta(days=d).total_seconds()))

@bot.command()
async def listTypes(ctx):
    """Shows the valid possible question types"""
    await ctx.send(f"""
    ```
╔════════════════╗
║ Question Types ║ 
╠════════════════╣
║ ARR            ║
║ LL             ║
║ HASHING        ║
║ TWOPOINTER     ║
║ BINARYSEARCH   ║
║ SLIDINGWINDOW  ║
║ TREES          ║
║ TRIES          ║
║ BACKTRACKING   ║
║ BFS            ║
║ DFS            ║
║ RECURSION      ║
║ HEAPS          ║
║ GRAPHS         ║
║ GREEDY         ║
║ GRAPHS         ║
╚════════════════╝```
    """)

@bot.command()
async def addSubmission(ctx):
    """Add another attempt to an exisiting question already being tracked by the LCM"""

    def check(m):
        return m.channel == ctx.channel and m.author == ctx.author

    await ctx.send("```What is the Question ID Number? Enter '?ShowQuestions' to find ID Number```")
    QID = ( await bot.wait_for('message', check=check) ).content
    if not QID.isdigit():
        await ctx.send("Try again!")

    data = await promptSub(ctx, QID)
    if data == None:
        return

    await ADB.insertTable("QuestionHistory", data)
    await ADB.updateUser(ctx.author.id)

    #NOTE: TO REMOVE
    print("Tables after adding a submission")
    await ADB.printAllTables()

#FIX: Don't allow user to run command twice if one is still being executed
@bot.command()
async def addQuestion(ctx, QID: str, NAME: str, DIFF: str, TYPE: str):
    """Add Question and Question Attempt for the LCM-bot to track"""
    if not checkAddQuestionInputFormat(QID, NAME, DIFF, TYPE):
        await ctx.send("""
    ```Please try again!
    ?addQuestion <ID> <NAME> <DIFFICULTY> <TYPE>
        > ID  :       INT 
        > Name:       STR
        > Difficulty: E/M/H
        > Type:       ?listTypes```
    """)
        return
    
    #NOTE: Adhere to..
    # At first Insertion, create user and first submission aswell
    # Submissions must always have accompanyuing Question In bank
    # Must always have existing user
    # No duplicate users


    await ADB.insertTable("Users", (ctx.author.id, -1 , -1 , int(RETRY_TIME_WINDOW.total_seconds()) ) )
    bankData = [int(QID), NAME, DIFF, TYPE, ctx.author.id]
    await ADB.insertTable("QuestionBank", tuple(bankData))
    submitData = await promptSub(ctx, QID)
    if submitData:
        await ADB.insertTable("QuestionHistory", tuple(submitData))
    await ADB.updateUser(ctx.author.id)

    print("Tables at end of 'AddQuestion' Command function")
    await ADB.printAllTables()

# -- [Modiefer Commands] --
# TEST:
#TODO: Add Update NOtes/Code
# ?UpdateQuestion
@bot.command()
async def update(ctx, qid):

    def check(m):
        return m.channel == ctx.channel and m.author == ctx.author
    await ctx.send("```new Name, Difficulty, or Type?```")
    CHANGE_TYPE= (await bot.wait_for('message', check=check)).content
    if CHANGE_TYPE not in ["Name", "Diffculty", "QuestonType"]:
        await ctx.send("Wrong options, try again!")
        return

    await ctx.send(f"```What is the new {CHANGE_TYPE}?```") 
    CHANGE_VALUE = ( await bot.wait_for('message', check=check) ).content

    await ADB.updateQuestion(ctx.author.id, qid, CHANGE_TYPE, CHANGE_VALUE)
    await ADB.printAllTables()

    #add exception
    await ctx.send(f"New {CHANGE_TYPE} Updated to {CHANGE_VALUE}")

# ?DeleteQuestion
@bot.command()
async def cmd_DeleteQuestion(ctx):
    pass

# -- [Getter Commands] --
#TODO: 
# - ?getupcoming, ?todo, ?all, ?completed, ?show <QID>
# - User Stats Display
# - Move helper functiosn and constants into seperate file
# - Table for submission may be too large, create more getters for notes and code

qheader, qfooter, sheader, sfooter = ("""
╔═════╦════════╦════════╦════════════╗
║ QID ║  NAME  ║  DIFF  ║    TYPE    ║
╠═════╬════════╬════════╬════════════╣
""",
"""
╚═════╩════════╩════════╩════════════╝
""",
"""
use ?submission <#> for more details
╔═════╦════════════╦════════════╦══════╗
║  #  ║  Attempted ║  To Retry  ║ Pass ║
╠═════╬════════════╬════════════╬══════╣
""",
"""
╚═════╩════════════╩════════════╩══════╝
""")

def questionTableFormatter(items):
    diff = {"E": "EASY", "M": "MED", "H": "HARD"}
    row_format ="║ {:^4}║ {:6s} ║  {:^4s}  ║ {:^10s} ║"
    dataString = ""
    dataString += qheader

    for item in items:
        QID, NAME, DIFF, TYPE = item
        DIFF = diff[DIFF]
        if len(NAME) > 6:
            NAME = NAME[0:5]
            NAME += '-'
        elif len(TYPE) > 10:
            TYPE = TYPE[0:9]
            TYPE += '-'
        dataString += row_format.format(QID, NAME, DIFF, TYPE) + '\n'
    dataString = dataString.rstrip() # Remove trailing 
    dataString += qfooter
    return dataString


#Can prob combine two function below:
@bot.command()
async def getUpcoming(ctx):
    """Displays previously failed questions"""
    items = await ADB.getUpcoming(ctx.author.id)
    print(items)
    await ctx.send("Questions that should be reattempted:")
    if items == []:
        await ctx.send("Nothing to reattempt :-)")
    else:
        await ctx.send(f"```{questionTableFormatter(items)}```")


def submissionTableFormatter(items):
    row_format ="║{:^5}║{:^12s}║{:^12s}║ {:5s}║"
    dataString = ""
    dataString += sheader
    for item in items:
        QID, ATTMP, RETRY, PASS = item
        print(f"pass = {PASS}")
        ATTMP = ATTMP.split()[0]
        RETRY = RETRY.split()[0]
        PASS = "YES" if PASS == 1 else "NO" 
        print(QID, ATTMP, RETRY, PASS)
        dataString += row_format.format(QID, ATTMP, RETRY, PASS) + "\n"
    dataString = dataString.rstrip() # Remove trailing 
    dataString += sfooter
    return dataString

# ?Todo
@bot.command()
async def todo(ctx):
    #Formatting
    items = await ADB.getTodoToday(ctx.author.id)
    print(items)
    await ctx.send("retry these questions today:")
    if items == []:
        await ctx.send("No questions to redo today :-)")
    else:
        await ctx.send(f"```{questionTableFormatter(items)}```")

#TEST:
@bot.command()
async def history(ctx, QID):
    """Question ID's submission history"""
    # items = await ADB.getSubmissions(ctx.author.id, QID)
    items = await ADB.getSubmissions(USER_ID, QID)
    print(items)
    await ctx.send(f"```Question {QID}'s History:\n{submissionTableFormatter(items)}```")

@bot.command()
async def submission(ctx, HID):
    # NOTES = (await ADB.getRowValue(USER_ID, HID, "Notes", "QuestionHistory"))
    # CODE  = (await ADB.getRowValue(USER_ID, HID, "Code", "QuestionHistory"))

    NOTES = ADB.getRowValue(ctx.author.id, HID, "Notes", "QuestionHistory")
    CODE  = ADB.getRowValue(ctx.author.id, HID, "Code", "QuestionHistory")

    #BUG:
    await ctx.send(f"```Notes:\n{NOTES[0]}```")
    await ctx.send(f"```Code:\n{CODE[0]}```")

@bot.command()
async def completed(ctx):
    """All of user's completed Questions"""
    items = await ADB.getCompleted(ctx.author.id)
    await ctx.send(f"```You have compelted the following questions\n{questionTableFormatter(items)}```")

# -- USER DISPLAY

@bot.command()
async def myStats(ctx):
    """Displays amount of questions user completed and attempted"""
    completed, attempted = await ADB.getUserStats(ctx.author.id)
    await ctx.send(f"```{completed} completed out of {attempted} attempted```")


# -- [ ERROR HANDLING ] --
# async def on_command_error(self, ctx: commands.Context, error):
#     #Error Handling
#     if isinstance(error, commands.MissingRequiredArgument):
#         await ctx.send(f"'{}' is a required argument")

# bot.on_command_error = on_command_error
bot.run(BOT_TOKEN)
