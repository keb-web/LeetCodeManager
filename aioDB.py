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
# 3. Test Functions and Debug
# 4. Add Docstrings


#TODO: discord.py cmd functions
#retryNotification() -> send notificaiton to User with User_ID
#adjustRetryWindow() -> default = 2 days, allow for user to adjust
#                    -> Requires additional column of User Table

async def getRowValue(UID, HID, Value, TableName):
    async with aiosqlite.connect("questions.db") as db:
        cmd = f"SELECT {Value} FROM {TableName} WHERE History_ID = ? AND User_ID = ?"
        # print(cmd)
        async with db.execute(cmd, (HID, UID)) as cursor:
            return (await cursor.fetchone())

async def getCompleted(UID):
    async with aiosqlite.connect("questions.db") as db:
        async with db.execute("""
        SELECT 
            Question_ID, Name, Difficulty, QuestionType
        FROM QuestionBank
        WHERE Question_ID IN (
            SELECT Question_ID
            FROM QuestionHistory
            WHERE User_ID = ?
            AND Completed = 1
        )
        """, (UID,)) as cursor:
            return (await cursor.fetchall())

#TODO:
#TEST: connected
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
#TEST: connected
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
            SELECT
                Question_ID, Name, Difficulty, QuestionType
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

async def getSubmissions(UID, QID):
    async with aiosqlite.connect("questions.db") as db:
        async with db.execute("""
        SELECT
            History_ID, date_attempted, retry_date, Completed
        FROM QuestionHistory
        WHERE
            User_ID = ? AND Question_ID = ? 
        """, (UID, QID)) as cursor:
            return await cursor.fetchall()



#TEST:
#TODO: Add feature where questions upcoming array is organized by retry date (closest upcoming)
#BUG: Prints upcoming for ALL USERS
async def getUpcoming(UID):
    """
    Returns an unsorted list of Upcoming Questions to be Redone
    :param UID: User_ID
    """
    print(f"userid: {UID}")
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

async def getUserStats(UID):
    """
    getter to display User's completed and attempted scores
    :param UID: User_ID
    """
    async with aiosqlite.connect("questions.db") as db:
        async with db.execute("""
            SELECT Total_Completed, Total_Attempted FROM Users
            WHERE User_ID = ?
        """, (UID,)) as cursor:
            row = await cursor.fetchone()
            if row:
                attempted, completed= row
                return (completed, attempted)
            else:
                print("User ID not Found")
                return (None, None)

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

        # #NOTE: remove later
        # async with db.execute(f"SELECT * FROM Users") as cursor:
        #     rows = await cursor.fetchall()
        #     for r in rows:
        #         print(r)

async def updateQuestion(UID, QID, attr, value):
    """
    Updates user's Name/Diff/Type
    """
    async with aiosqlite.connect("questions.db") as db:
        prompt = f"UPDATE QuestionBank SET {attr} = ? WHERE User_ID = ? AND  Question_ID = ?"
        await db.execute(prompt,(value, UID, QID))
        await db.commit()

#TODO: Sync with discord client input
# CONNECT
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
        print("tables created")

    #NOTE: Users
    # (User_ID, Total_Completed, Total_Attempted)
    user_data1 = (USER_ID, 1, 1, int( RETRY_TIME_WINDOW.total_seconds() ) )
    await insertTable("Users", user_data1)

    #NOTE: Question
    #QID, NAME, DIFF, TYPE, UID
    q1 = (1, "TWOSUM", "E", "ARRAY", USER_ID)
    q2 = (2, "3WOSUM", "E", "ARRAY", USER_ID)
    q3 = (3, "4WOSUM", "E", "ARRAY", USER_ID)
    q4 = (4, "5WOSUM", "H", "ARRAY", USER_ID)

    qa = (1, "TWOSUM", "H", "ARRAY", USER_ID2)
    await insertTable("QuestionBank", q1)
    await insertTable("QuestionBank", q2)
    await insertTable("QuestionBank", q3)
    await insertTable("QuestionBank", q4)

    await insertTable("QuestionBank", qa)

    #NOTE: Submission History
    #QID, COMP, CODE, DATE, RETRY DATE, NOTES, UID
    s1time = datetime.today() - timedelta(days = 2)
    s2time = datetime.today() - timedelta(days = 1)
    s3time = datetime.today() - timedelta(days = 0)
    s3time = datetime.today() - timedelta(days = 0)
    s1 = (1, False, "None", s1time, s1time + RETRY_TIME_WINDOW, "Notes", USER_ID)
    s21 = (1, True, "For i in window\n", s2time, s2time + RETRY_TIME_WINDOW, "YOU FOIUND ME", USER_ID)
    s2 = (2, True, "None", s2time, s2time + RETRY_TIME_WINDOW, "Notes", USER_ID)
    s3 = (3, True, "None", s3time, s3time + RETRY_TIME_WINDOW, "Notes", USER_ID)
    s4 = (4, True, "None", s3time, s3time + RETRY_TIME_WINDOW, "Notes", USER_ID)

    sa = (1, True, "None", s3time, s3time + RETRY_TIME_WINDOW, "Notes", USER_ID2)

    await insertTable("QuestionHistory", s1)
    await insertTable("QuestionHistory", s21)
    await insertTable("QuestionHistory", s2)
    await insertTable("QuestionHistory", s3)
    await insertTable("QuestionHistory", s4)

    await insertTable("QuestionHistory", sa)

    print("----  printing all tables  ----")
    await printAllTables()
    print("--- end of manual test ---")

    # print(await getSubmissions(USER_ID, 1))

    # print(await getCompleted(USER_ID))

#BUG: Question History Insertion without exiting QID
asyncio.run(main())
