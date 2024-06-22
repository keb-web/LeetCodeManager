import aiosqlite
import asyncio
#TODO :remove os later
import os
from datetime import date, datetime, timedelta
from schema import QUESTION_BANK, QUESTION_HISTORY, USERS, RETRY_TIME_WINDOW, USER_ID, USER_ID2

#TODO: 
# 1. Adjust tables
#    - [x] Retry Boolean column --> not needed, just check if completed = false
#    - [x] User retry_window column
#    - [ ] Retry (dynamically updated) date column  --> update daily before notify()
# 2. Finish up Function Implementation
#       optional Functions
#           -> Update USERS Retry_Window column
#           -> 
# 3. Test Functions and Debug
# 4. Add Docstrings


#TODO: discord.py cmd functions
#retryNotification() -> send notificaiton to User with User_ID
#adjustRetryWindow() -> default = 2 days, allow for user to adjust
#                    -> Requires additional column of User Table

#TODO:
#TEST:
async def updateRetryDate(UID, newRetry):
    async with aiosqlite.connect("questions.db") as db:
        await db.execute("""
        UPDATE Users
        SET Retry_Window = ?
        WHERE
        User_ID = ?
        """, (newRetry, UID))
        await db.commit()
        await printAllTables()

#TODO:
#TEST:
async def getRetryWindow(UID):
    """
    return User's Retry_Window Value (INTEGER / timedelta?? )
    """
    async with aiosqlite.connect("questions.db") as db:
        async with db.execute("""
        SELECT Retry_Window
        FROM Users
        WHERE
            User_ID = ?
        """,(UID,)) as cursor:
            value = await cursor.fetchone()
            if value:
                # retry_window = timedelta(seconds = value[0])
                retry_window = value[0]
                print(f"Retry_Window for user {UID}: {retry_window}")
                return timedelta(seconds = retry_window)
            else:
                print(f"No Retry_Window found for user {UID}.")
                return None
#TODO:
#TEST:
async def getTodoToday(UID):
    """
    return data row if date.today() = Uncompleted Questionions + RETRY_TIME_WINDOW
    Returns Questions that are due today
    """
    currentDay = datetime.combine(date.today(), datetime.min.time())
    async with aiosqlite.connect("questions.db") as db:
        async with db.execute("""
            SELECT *
            FROM QuestionBank
            WHERE Question_ID IN (
                SELECT Question_ID
                FROM QuestionHistory
                WHERE User_ID = ?
                AND retry_date = ?
                AND Completed = 0
            )
        """,(UID, currentDay)) as cursor:
            return await cursor.fetchall()

#TEST:
#TODO: Add feature where questions upcoming array is organized by retry date (closest upcoming)
async def getUpcoming(UID):
    """
    Returns an unsorted list of Upcoming Questions to be Redone
    :param UID: User_ID
    """
    # Gets current day at midnight
    currentDay = datetime.combine(date.today(), datetime.min.time())
    async with aiosqlite.connect("questions.db") as db:
        #NOTE: OBSIDIAN: Log difference between '=' and 'IN' for the subquery "WHERE QID IN ..."

        async with db.execute("""
        SELECT 
            Question_ID, Name, Difficulty, QuestionType
        FROM QuestionBank
        WHERE Question_ID IN (
            SELECT Question_ID
            FROM QuestionHistory
            WHERE User_ID = ?
            AND retry_date >= ?
            AND Completed = 0
        )
        """, (UID, currentDay)) as cursor:
            return await cursor.fetchall()

#Add get User Retry_Window
async def getUserStats(UID):
    """
    getter to display User's completed and attempted scores
    :param UID: User_ID
    """
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
        
        

#Add User Retry_Window Update
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
            print(f"newTotal: {newTotal}")

        #determine total questions completed from QuestionHistory
        #   Count total # of rows that..
        #   Are User_ID's latest attempt for EACH question
        #   Only count if they are the latest and completed

        #NOTE: Learn Partition
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
            print(f"newCompleted: {newCompleted}")

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

#TODO: Sync with discord client input
async def updateQuestion(UID, QID):
    """

    """
    newName = "newName"
    newDiff = "newDiff"
    newType = "newType"

    async with aiosqlite.connect("questions.db") as db:
        await db.execute("""
        UPDATE QuestionBank
        SET Name = ?,
            Difficulty = ?,
            QuestionType = ?
        WHERE User_ID = ? AND Question_ID = ?
        """,(newName, newDiff, newType, UID, QID))
        await db.commit()

#TODO: Sync with discord client input
async def updateSubmission(UID, QID):
    """
    Updates latests submission in QuestionHistory based on QuestionID, UserID, and Latest value for date_attempted
    :param UID: User_ID
    :param QID: Question_ID
    """
    # Temp change variables NOTE: delete later!!
    newComp = True
    newCode = "updoot"
    newDate = "updoot"
    newNotes = "updoot"

    async with aiosqlite.connect("questions.db") as db:
        await db.execute("""
        UPDATE QuestionHistory
        SET Completed = ?,
            Code = ?,
            date_attempted = ?,
            Notes = ?
        WHERE History_ID = (
            SELECT History_ID
            FROM QuestionHistory
            WHERE User_ID = ? AND Question_ID = ?
            ORDER BY date_attempted DESC
            LIMIT 1
        )
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
        

async def removeLatestSubmission(UID, QID):
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
        WHERE User_ID LIKE ?
        AND Question_ID LIKE ?
        LIMIT 1
        )
        """, (UID, QID))

        # remove question from questionbank if no history
        await db.execute(f"""
        DELETE FROM QuestionBank 
        WHERE NOT EXISTS (
        SELECT * FROM QuestionHistory
        WHERE User_ID LIKE ?
        AND Question_ID LIKE ?
        )
        """, (UID, QID))

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


#Can only checkexisintng for one column
async def checkExisting(tableName, attr, value):
    async with aiosqlite.connect("questions.db") as db:
        try:
            query = f"SELECT EXISTS(SELECT 1 FROM {tableName} WHERE {attr} = ?)"
            print(query)
            async with db.execute(query, (value,)) as cursor:
                result = await cursor.fetchone()
                if result is None:
                    return False
                return True if result[0] else False
        except Exception as e:
            print(f"An error occured: {e}")
            return False

#TODO: Check existing
# NOTE: when initially inserting into questionbank, also insert fisrt submission into QHist
async def insertTable(type, data):
    async with aiosqlite.connect("questions.db") as db:
        match type:
            case "QuestionBank":
                #Insert only if QID doesn't exist for that user
                Question_ID, User_ID = data[0], data[-1]

                async with db.execute("""SELECT EXISTS(
                SELECT 1 FROM QuestionBank 
                WHERE Question_ID = ?
                AND User_ID = ?
                )
                """, (Question_ID, User_ID)) as cursor:
                    result = await cursor.fetchone()
                    if result is None:
                        print("result is none")
                        return
                    elif result[0] == True:
                        print("Cannot insert")
                    else:
                        await db.execute("INSERT INTO QuestionBank (Question_ID, Name, Difficulty, QuestionType, User_ID) VALUES ( ?, ?, ?, ?, ?)", (data))
            case "QuestionHistory":
                #insert into tablehistory only if the question existss in questionBank
                #TODO: figure out how this works
                #TODO: If not exist, notify user in discord
                await db.execute("""INSERT INTO QuestionHistory ( Question_ID, Completed, Code, date_attempted, retry_date, Notes, User_ID)
                                    SELECT ?, ?, ?, ?, ?, ?, ?
                                    WHERE EXISTS (
                                        SELECT 1 FROM QuestionBank 
                                        WHERE Question_ID = ?
                                        AND User_ID = ? 
                                    )
                                 """, (*data, data[0], data[6]))
            case "Users":
                #Insert User only if it doesn't exist yet
                await db.execute("INSERT OR IGNORE INTO Users (User_ID, Total_Completed, Total_Attempted, Retry_Window) VALUES (?, ?, ?, ?)", (data))
            case _:
                print("No matching table to insert")
                return
        await db.commit()

        # # Query & Print  NOTE: Remove later
        # print("bank:")
        # async with db.execute(f"SELECT * FROM QuestionBank") as cursor:
        #     rows = await cursor.fetchall()
        #     for r in rows:
        #         print(r)
        #     print("---")
        # print("hist:")
        # async with db.execute(f"SELECT * FROM QuestionHistory") as cursor:
        #     rows = await cursor.fetchall()
        #     for r in rows:
        #         print(r)
        #     print("---")
        # print("Users:")
        # async with db.execute(f"SELECT * FROM Users") as cursor:
        #     rows = await cursor.fetchall()
        #     for r in rows:
        #         print(r)
        #     print("---")

#NOTE: for testing, will be linked with discord.py when functional
async def main():
    #Creating tables
    async with aiosqlite.connect("questions.db") as db:
        await db.execute(QUESTION_BANK)
        await db.execute(QUESTION_HISTORY)
        await db.execute(USERS)
        await db.commit()

    # print("tables created")

    #NOTE: Users

    # # (User_ID, Total_Completed, Total_Attempted)
    # user_data1 = (USER_ID, 1, 1, int( RETRY_TIME_WINDOW.total_seconds() ) )
    # await insertTable("Users", user_data1)
    # user_data2 = (USER_ID2, 1, 1, int(RETRY_TIME_WINDOW.total_seconds()) )
    # await insertTable("Users", user_data2, )
    #
    # # #TEST:
    # # #NOTE: Question
    # # # # QID, NAME, DIFF, TYPE, UID
    # # q1 = (1, "TWOSUM", "EASY", "ARRAY", USER_ID)
    # # q4 = (1, "TWOSUM", "EASY", "ARRAY", USER_ID2)
    # # q2 = (2, "THREESUM", "MED", "ARRAY", USER_ID)
    # # q3 = (2, "THREESUM", "MED", "ARRAY", USER_ID2)
    # #
    # # # q3 = (3, "FOURSUM", "HARD", "ARRAY", USER_ID)
    # await insertTable("QuestionBank", q1)
    # await insertTable("QuestionBank", q1)
    # await insertTable("QuestionBank", q2)
    # await insertTable("QuestionBank", q2)
    # await insertTable("QuestionBank", q3)
    # await insertTable("QuestionBank", q3)
    # await insertTable("QuestionBank", q4)
    # # print(await checkExisting("QuestionBank", "Question_ID", "1"))
    # # print(await checkExisting("QuestionBank", "Question_ID", "2"))
    # # print(await checkExisting("QuestionBank", "Question_ID", "3"))
    # # # await insertTable("QuestionBank", q3)
    #
    #NOTE: Users

    # (User_ID, Total_Completed, Total_Attempted)
    # user_data1 = (USER_ID, 1, 1, int( RETRY_TIME_WINDOW.total_seconds() ) )
    # print(int(RETRY_TIME_WINDOW.total_seconds()))
    # await insertTable("Users", user_data1)
    # user_data2 = (USER_ID2, 1, 1, int(RETRY_TIME_WINDOW.total_seconds()) )
    # await insertTable("Users", user_data2, )
    #
    # #NOTE: Submission History
    # # QID, COMP, CODE, DATE, RETRY DATE, NOTES, UID
    #
    # s1time = datetime.today() - timedelta(days = 3)
    # s3time = datetime.today() + timedelta(days = 3)
    # s4time = datetime.today() + timedelta(days = 4)
    #
    # s1 = (1, False, "None", s1time, s1time + RETRY_TIME_WINDOW, "Notes", USER_ID)
    # s2 = (1, False, "None", s4time, s4time + RETRY_TIME_WINDOW, "Notes", USER_ID)
    #
    # s3 = (2, False, "None", s1time, s1time + RETRY_TIME_WINDOW, "Notes", USER_ID2)
    # s4 = (2, False, "None", s3time, s3time + RETRY_TIME_WINDOW, "Notes", USER_ID2)
    #
    # await insertTable("QuestionHistory", s1)
    # await insertTable("QuestionHistory", s2)
    # await insertTable("QuestionHistory", s3)
    # await insertTable("QuestionHistory", s4)
    #
    # #NOTE: 
    # # [OTHER FUNCTIONS]
    # # agetRetryWindow(USER_ID)
    # # await getUpcoming(USER_ID2)
    #
    #
    #
    # print("----  printing all tables  ----")
    # await printAllTables()

    # #NOTE: temprorary -> remove db for testingtemp
    # os.remove("questions.db")

#BUG: Question History Insertion without exiting QID
#TODO : IF USER NOT FOUND AT INSERTION, Create and insert user with USERID
#NOTE: Initial QuestionLOG must be accompanied with initial submission log

asyncio.run(main())
