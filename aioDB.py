import aiosqlite
import asyncio
#TODO :remove os later
import os
from datetime import date, timedelta
from schema import QUESTION_BANK, QUESTION_HISTORY, USERS, USER_ID, USER_ID2

async def getUpcoming():
    pass

async def todo():
    pass

#TEST:
async def userStats(UID):
    completed = -1
    attempted= -1
    async with aiosqlite.connect("questions.db") as db:
        async with db.execute("""
            SELECT Total_Completed, Total_Attempted FROM Users
            WHERE User_ID = ?
        """, (UID,)) as cursor:
            row = await cursor.fetchone()
            if row:
                completed, attempted = row
            else:
                print("User ID not Found")

    #NOTE: will sende out as discord msg, or return for command
    print(f"completed: {completed}, atttempted: {attempted}")
        
        

async def updateUser(UID):
    """
    Updates Total Attempted and Total Complted
    CANNOT change UserID, it is dictated by discord.py
    :param UID: User ID (ctx.author.id)
    """

    print(f"updating user{UID}")
    async with aiosqlite.connect("questions.db") as db:
        #determine total questions attempted form QuestionBank
        async with db.execute("""
        SELECT COUNT(*)
        FROM QuestionBank
        WHERE User_ID = ?
        """,(UID,)) as cursor:
            newTotal = await cursor.fetchone()
            newTotal = newTotal[0] if newTotal else 0
            print(f"newTotal:{newTotal}")

        #determine total questions completed from QuestionHistory
        #   Count total # of rows that..
        #   Are User_ID's latest attempt for EACH question
        #   Only count if they are the latest and completed
        async with db.execute("""
        SELECT COUNT(*)
        FROM (
            SELECT *, MAX(date_attempted) OVER (PARTITION BY Question_ID) AS latest_attempt
            FROM QuestionHistory
            WHERE USER_ID = ?
        )
        WHERE date_attempted = latest_attempt and Completed = 1
        """,(UID,)) as cursor:
            newCompleted = await cursor.fetchone()
            newCompleted = newCompleted[0] if newCompleted else 0
            print(f"newCompleted{newCompleted}")

        #Update Users row, User_ID
        await db.execute("""
        UPDATE Users 
        SET Total_Completed = ?,
            Total_Attempted = ?
        WHERE
            User_ID = ?
        """,(newTotal, newCompleted, UID))

        await db.commit()

        #NOTE: remove later
        async with db.execute(f"SELECT * FROM Users") as cursor:
            rows = await cursor.fetchall()
            for r in rows:
                print(r)

#TEST:
async def updateQuestion(QID, UID):
    # Change Question

    # TODO: Get changes from discord command
    # Temp change variables NOTE: delete later!!
    newName = "newName"
    newDiff = "newDiff"
    newType = "newType"

    async with aiosqlite.connect("database.db") as db:
        await db.execute("""
        UPDATE QuestionBank
        SET Name = ?,
        Difficulty = ?,
        QuestionTyppe = ?
        WHERE User_ID = ? AND Question_ID = ?
        """,(newName, newDiff, newType, UID, QID))
        await db.commit()

#TEST:
async def updateSubmission(UID, QID):
    # TODO: Get changes from discord command
    # Temp change variables NOTE: delete later!!

    newComp = True
    newCode = "updoot"
    newDate = "updoot"
    newNotes = "updoot"

    async with aiosqlite.connect("database.db") as db:
        await db.execute("""
        UPDATE QuestionHistory
        SET Completed = ?,
            Code = ?,
            date_attempted = ?,
            Notes = ?
        WHERE User_ID = ? AND Question_ID = ?
        ORDER BY date_attempted DESC
        LIMIT 1
        """, (newComp, newCode, newDate, newNotes, UID, QID))

        await db.commit()

async def printAllTables():
    """
    Helper function that prints all contents of every table to assist with debugging
    """
    async with aiosqlite.connect("questions.db") as db:
        # Query & Print  NOTE: Remove later
        print("bank:")
        async with db.execute(f"SELECT * FROM QuestionBank") as cursor:
            rows = await cursor.fetchall()
            for r in rows:
                print(r)
        print("hist:")
        async with db.execute(f"SELECT * FROM QuestionHistory") as cursor:
            rows = await cursor.fetchall()
            for r in rows:
                print(r)
        print("Users:")
        async with db.execute(f"SELECT * FROM Users") as cursor:
            rows = await cursor.fetchall()
            for r in rows:
                print(r)

#remove question
#if has history, remove whole history
async def removeQuestion(value, userID):
    """
    Removes Question & Linked Question History
    :param value:  Question ID Value
    :param userID: discord user's account id  (cts.account.id)
    """

    print("Removing...")
    async with aiosqlite.connect("questions.db") as db:
        # Remove Question
        await db.execute(f"DELETE from QuestionBank WHERE Question_ID = ? AND User_ID = ?", (value, userID))
        
        # Remove Question Submission History
        await db.execute(f"DELETE from QuestionHistory WHERE Question_ID = ? AND User_ID = ?", (value ,userID))
        await db.commit()

        # #print Questionbank Table NOTE: Remove 
        # async with db.execute(f'SELECT * FROM QuestionBank') as cursor:
        #     rows = await cursor.fetchall()
        #     for r in rows:
        #         print(r)
        
        # #print QuestionHistory Table NOTE: Remove
        # async with db.execute(f'SELECT * FROM QuestionHistory') as cursor:
        #     rows = await cursor.fetchall()
        #     for r in rows:
        #         print(r)
        
#remove latest attempt
#remove from history until no more, then remove question entirely
#TEST: RemoveLatest if there is none
async def removeLatestSubmission(value, userID):
    """
    Removes latest submission from questionHistory based on 'date_attempted'
    Removes question from questionbank if no more submissions exist
    :param value:  Question ID Value
    :param userID: discord user's account id  (cts.account.id)
    """
    async with aiosqlite.connect("questions.db") as db:

        # remove latest submission
        await db.execute(f"""
        DELETE FROM QuestionHistory 
        WHERE date_attempted = (
        SELECT MAX(date_attempted) FROM QuestionHistory
        WHERE Question_ID LIKE ?
        AND User_ID LIKE ?
        LIMIT 1
        )
        """, (value, userID))

        # remove question from questionbank if no history
        await db.execute(f"""
        DELETE FROM QuestionBank 
        WHERE NOT EXISTS (
        SELECT * FROM QuestionHistory
        WHERE Question_ID LIKE ?
        AND User_ID LIKE ?
        )
        """, (value, userID))

        await db.commit()

        # print QuestionHistory by latest # NOTE: remove
        # print("QuestionHistory:")
        # async with db.execute(f"SELECT * FROM QuestionHistory ORDER BY date_attempted DESC") as cursor:
        #     rows = await cursor.fetchall()
        #     for r in rows:
        #         print(r)
        #
        # # print QuestionBank by latest # NOTE: remove
        # print("QuestionBank:")
        # async with db.execute(f"SELECT * FROM QuestionBank WHERE Question_ID = ? AND User_ID = ?", (value, userID)) as cursor:
        #     rows = await cursor.fetchall()
        #     for r in rows:
        #         print(r)

# NOTE: when initially inserting into questionbank, also insert fisrt submission into QHist
async def insertTable(type, data):
    print("Inserting...")
    async with aiosqlite.connect("questions.db") as db:
        match type:
            case "QuestionBank":
                await db.execute("INSERT INTO QuestionBank (Question_ID, Name, Difficulty, QuestionType, User_ID) VALUES ( ?, ?, ?, ?, ?)", (data))
            case "QuestionHistory":
                await db.execute("INSERT INTO QuestionHistory ( Question_ID, Completed, Code, Date_Attempted, Notes, User_ID) VALUES ( ?, ?, ?, ?, ?, ?)", (data))
            case "Users":
                await db.execute("INSERT OR IGNORE INTO Users (User_ID, Total_Completed, Total_Attempted) VALUES (?, ?, ?)", (data))
            case _:
                print("No matching table to insert")
                return
        await db.commit()

        #Query & Print  NOTE: Remove later
        # print("\tbank")
        # async with db.execute(f"SELECT * FROM QuestionBank") as cursor:
        #     rows = await cursor.fetchall()
        #     for r in rows:
        #         print(r)
        # print("\thist")
        # async with db.execute(f"SELECT * FROM QuestionHistory") as cursor:
        #     rows = await cursor.fetchall()
        #     for r in rows:
        #         print(r)
        # print("\tUsers")
        # async with db.execute(f"SELECT * FROM Users") as cursor:
        #     rows = await cursor.fetchall()
        #     for r in rows:
        #         print(r)

        
#NOTE: for testing, will be linked with discord.py when functional
async def main():
    #Creating tables
    async with aiosqlite.connect("questions.db") as db:
        await db.execute(QUESTION_BANK)
        await db.execute(QUESTION_HISTORY)
        await db.execute(USERS)
        await db.commit()

    #Question_ID, Name, Difficulty, QuestionType, User_ID
    question_data1 = (1, "TwoSum", "E", "Array", USER_ID)
    question_data2 = (2, "ThreeSum", "M", "Array", USER_ID)

    # History_ID, Question_ID, Completed, Code, Date_Attempted, Notes
    qHist_data1 = ( 1, False, "code goes here", date.today(), "This shit was hard!", USER_ID )
    qHist_data2 = ( 1, False, "code goes here", date.today() + timedelta(days=1), "This shit was hard-ish!", USER_ID )
    qHist_data3 = ( 1, False, "code goes here", date.today() + timedelta(days=2), "This shit was medium-hard!", USER_ID )
    qHist_data4 = ( 1, True, "code goes here", date.today() + timedelta(days=3), "This shit was easy!", USER_ID )

    qHist_data5 = ( 2, False, "code goes here", date.today() + timedelta(days=3), "idk :(", USER_ID )
    qHist_data6 = ( 2, True, "code goes here", date.today() + timedelta(days=4), "idk :(", USER_ID )
    qHist_data7 = ( 2, True, "updated code goes here", date.today() + timedelta(days=5), "more optimized solution", USER_ID )
    qHist_data8 = ( 2, False, "i forgot...", date.today() + timedelta(days=6), "forgot solution", USER_ID )

    #(User_ID, Total_Completed, Total_Attempted)
    user_data1 = (USER_ID, 1, 1)
    user_data2 = (USER_ID2, 1, 1)

    await insertTable( "QuestionBank", question_data1)
    await insertTable( "QuestionBank", question_data2)

    await insertTable( "QuestionHistory", qHist_data1)
    await insertTable( "QuestionHistory", qHist_data2)
    await insertTable( "QuestionHistory", qHist_data3)
    await insertTable( "QuestionHistory", qHist_data4)

    await insertTable( "QuestionHistory", qHist_data5)
    await insertTable( "QuestionHistory", qHist_data6)
    await insertTable( "QuestionHistory", qHist_data7)
    await insertTable( "QuestionHistory", qHist_data8)

    await insertTable( "Users", user_data1)
    await insertTable( "Users", user_data2)

    await updateUser(USER_ID)

    print("printing all tables")
    await printAllTables()

    # temprorary -> remove db for testing
    os.remove("questions.db")



asyncio.run(main())
