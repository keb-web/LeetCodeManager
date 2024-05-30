from os import walk
import sqlite3
from sqlite3.dbapi2 import Row
from typing import List
from datetime import  date

# TODO: time attributes and loading history
# TODO: History -> update history with new submission
# TODO: History -> Link Question ID to History ID

class q:
    # WARNING: Lsp throws error
    # TODO: Remove Date attribute
    def __init__(self, ID: int, Name: str, Difficulty: str, Type: str) -> None:
        self.ID = ID
        self.Name = Name
        self.Difficulty = Difficulty
        self.Type = Type

    def getData(self) -> tuple:
        return (self.ID, self.Name, self.Difficulty, self.Type)

    def __str__(self):
        return (f"{self.ID}, {self.Name}, {self.Difficulty}, {self.Type}")


def createDatabase():
    con = sqlite3.connect("questions.db")
    return con


def createTable(cur: sqlite3.Cursor, tableName : str, attr: List[str]) -> None:
    columns = ', '.join(attr)
    # print("__Creating table__")
    # print("__Creating table with:__")
    # print(columns)
    cmd = f"CREATE TABLE IF NOT EXISTS {tableName}({columns})"
    cur.execute(cmd)


# TODO: Debug 'checkExisting' due to change in datatype (val1 -> string to Int)
def checkExisting(cur: sqlite3.Cursor, tableName: str, cond1: str, val1: int)-> bool:
    # print("__CHECKEXISTING__")
    print(cond1, val1)
    cmd = f"SELECT EXISTS(SELECT 1 FROM {tableName} WHERE {cond1} = (?) )"
    cur.execute(cmd, str(val1))
    result = cur.fetchone()
    return result[0]
    

# add to question history
"""
            "History_ID INTEGER PRIMARY KEY AUTOINCREMENT",
            "Question_ID INTEGER",
            "Compelted BOOLEAN NOT NULL",
            "Code TEXT",
            "date_attempted DATETIME",
            "Notes TEXT",
            "FOREIGN KEY (Question_ID) REFERENCES QuestionBank(Question_ID)"
"""
# FIX:  DeprecationWarning: The default date adapter is deprecated as of Python 3.12; see the sqlite3 documentation for suggested replacement recipes
# FIX: History appended multiple times. Check existing??

def updateQHist(cur: sqlite3.Cursor, QID: int) -> None:
    # TODO: Update: Date Taken and/or Completed (if Applicable)
    # TODO: Get user Input

    # NOTE: by default dateAttempted to today()
    # TODO: USER INPUT: "Did you attempt today? Y/N"
    #if 'N', Prompt datetime input

    # id, name, difficulty, type, date
    tableName = "QuestionHistory"
    # id = QID
    dateAttempted = date.today()
    print("Date Attempted: ", dateAttempted)
    # NOTE: faking user inputs: completed, code, notes
    tempComp = True
    tempCode = "hello('World!')" #(optional)
    tempNotes = "this shit was hard!"
    # ------------------------------------------------

    cmd = f"INSERT INTO QuestionHistory VALUES(?, ?, ?, ?, ?, ?)"
    cur.execute(cmd, (None, QID, tempComp, tempCode, dateAttempted, tempNotes))

    # FIX: Verify Insertion
    # NOTE: change attrib for debugging
    attrib = "date_attempted"
    cmd = f"SELECT {attrib} from {tableName}"
    res = cur.execute(cmd)
    print(res.fetchall())




# TODO: change "Question_ID dynamically"
# FIX: add to questionBank and QuestionHistory
def addQuestion(cur: sqlite3.Cursor, tableName: str, question: q) -> None:

    if checkExisting(cur, tableName, "Question_ID", question.ID):
        print("Update Question History:")
        # Add row to Question history
        updateQHist(cur, question.ID)
        return

    
    print("Adding Question to QuestionBank:")

    data = question.getData()
    # FIX: Remove Later
    print("data:", data)

    placeholder = ', '.join(['?' for _ in range (len(data))])
    cmd = f"INSERT INTO {tableName} VALUES({placeholder})"
    cur.execute(cmd, data)

    # FIX: Remove later

    # FIX: verify insertion
    cmd = f"SELECT Name from {tableName}"
    res = cur.execute(cmd)
    print(res.fetchall())


def removeQuestion(cur: sqlite3.Cursor, tableName: str, attrib: str, value: str) -> None:
    """
    :param atrib: Column typle
    :param value: Matching value in column
    """

    print("__Removing__")
    cmd = f"DELETE from {tableName} WHERE {attrib} LIKE '{value}'"
    print(cmd)
    cur.execute(cmd)

    # check funtionality

#TODO: Alter Question
def alterQuestion():

    pass



def printMasterSchema(cur: sqlite3.Cursor, attr: str = "name")-> None:
    """
    printMasterSchema prints all table [attr] contained in the Schema Table
    :param cur: Database Cursor
    :param attr: By default is name. The attribute of each table that is printed
    """
    print("All tables (Master Schema): ")
    cmd = f"SELECT {attr} FROM sqlite_master"
    res = cur.execute(cmd)
    for v in res.fetchall():
        print(f"\t{v[0]}")
    print()


def printTableColumns(cur: sqlite3.Cursor ):
    pass


#TODO: Add colors
#TODO: Check "QuestionHistory" table compatability
def printTable(cur: sqlite3.Cursor, tableName: str) -> None:
    cmd = f"SELECT rowid, * FROM {tableName}"
    cur.execute(cmd)
    items = cur.fetchall()

    headers = [" ROW ID", "QID", "NAME", "DIFFICULTY", "TYPE"]
    widths = [8, 5, 12, 11, 8]

    # Create the format string using the widths
    header_format = f"{headers[0]:^{widths[0]}} | {headers[1]:^{widths[1]}} | {headers[2]:<{widths[2]}} | {headers[3]:<{widths[3]}} | {headers[4]:<{widths[4]}}"
    separator = "-" * (sum(widths) + len(widths) * 3 - 1)  # Total width of the table including separators
    row_format = f"{{:^{widths[0]}}} | {{:^{widths[1]}}} | {{:<{widths[2]}}} | {{:<{widths[3]}}} | {{:<{widths[4]}}}"

    # Print the header and separator
    print(f"\n{tableName}:")
    print(separator)
    print(header_format)
    print(separator)


    # Print each row using the row format
    for item in items:
        print(row_format.format(item[0], item[1], item[2], item[3], item[4]))



# FIX: Can't Test until Question Add for both tables is fixed
# TODO: TEST printRow function, Add is currently fixed
def printRow(cur: sqlite3.Cursor, tableName:str, id: int) -> None:
    cmd = f"SELECT {id} FROM {tableName}"
    cur.execute(cmd)
    item = cur.fetchone()
    print(item)

def printCol(cur: sqlite3.Cursor, tableName:str, id:int) -> None:
    pass

# TABLE: "QuestionBank"
# Question_ID INTEGER PRIMARY KEY
# Name TEXT NOT NULL
# Difficulty TEXT NOT NULL
# QuestionType TEXT NOT NULL

# TABLE: QuestionHistory
# History_ID INTEGER PRIMARY KEY AUTOINCREMENT
# Question_ID INTEGER FOREIGN KEY
# Compelted BOOLEAN NOT NULL
# Attempt_Number INTEGER
# Code TEXT 
# date_attempted DATETIME 
# Notes TEXT 
# FOREIGN KEY (Question_ID) REFERENCES QuestionBank(Question_ID)

def main():
    connection = createDatabase()
    cursor = connection.cursor()

    # NOTE: For Testing... Remove later

    createTable( cursor,
                "QuestionBank", [
                "Question_ID INTEGER PRIMARY KEY",
                "Name TEXT NOT NULL",
                "Difficulty TEXT NOT NULL",
                "QuestionType TEXT NOT NULL"
                ])

    createTable( cursor,
                "QuestionHistory", [
                "History_ID INTEGER PRIMARY KEY AUTOINCREMENT",
                "Question_ID INTEGER",
                "Compelted BOOLEAN NOT NULL",
                "Code TEXT",
                "date_attempted DATETIME",
                "Notes TEXT",
                "FOREIGN KEY (Question_ID) REFERENCES QuestionBank(Question_ID)"
                ])

    printMasterSchema(cursor)

    q1= q(0, "TwoSum", "Easy", "Arrays")
    q2= q(1, "ThreeSum", "Medium", "LL")

    # dupe = q(ID, Name, Difficulty, QuestionType)
    # testQuestion2 = q("1", "THREESUM", "Medium", "Arrays")
    # testQuestionRemove = q("2", "TODELETE", "HARD", "TREES")

    addQuestion(cursor, "QuestionBank", q1)
    addQuestion(cursor, "QuestionBank", q2)
    # addQuestion(cursor, TableName, testQuestion2)
    # addQuestion(cursor, TableName, dupe)
    # addQuestion(cursor, TableName, testQuestionRemove)

    printTable(cursor, "QuestionBank")

    connection.commit()
    connection.close()

if __name__ == "__main__":
    main()
