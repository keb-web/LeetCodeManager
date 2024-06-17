#FIX: adjust program to make QuestionID AutoIncrement ?
# OR Connect to LC Question DB (JS??)

from datetime import timedelta

QUESTION_BANK = """
CREATE TABLE IF NOT EXISTS QuestionBank (
    Entry_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Question_ID INTEGER,
    Name TEXT NOT NULL,
    Difficulty TEXT NOT NULL,
    QuestionType TEXT NOT NULL,
    User_ID INTEGER,
    FOREIGN KEY (User_ID) REFERENCES Users(User_ID)
)
"""

#DATETIME instead of DATE
QUESTION_HISTORY = """
CREATE TABLE IF NOT EXISTS QuestionHistory (
    History_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Question_ID INTEGER,
    Completed BOOLEAN NOT NULL,
    Code TEXT,
    date_attempted DATETIME,
    retry_date DATETIME,
    Notes TEXT,
    User_ID INTEGER,
    FOREIGN KEY (Question_ID) REFERENCES QuestionBank(Question_ID),
    FOREIGN KEY (User_ID) REFERENCES Users(User_ID)
)
"""

#TODO: Future feature: Allow for users to adjust RETRY_TIME_WINDOW with a new row stored in "Users" Table
USERS = """
CREATE TABLE IF NOT EXISTS Users (
    User_ID INTEGER PRIMARY KEY,
    Total_Completed INTEGER,
    Total_Attempted INTEGER,
    Retry_Window INTEGER
)
"""

USER_ID =  "800858"
USER_ID2 = "12312"
# ctx.author.id

RETRY_TIME_WINDOW = timedelta(days=2)
