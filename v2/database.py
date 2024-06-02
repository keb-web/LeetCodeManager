from os import sep, walk
from re import search
import sqlite3
from sqlite3.dbapi2 import Row
from typing import List, Tuple
from datetime import  date

# TODO: time attributes and loading history
# TODO: History -> update history with new submission
# TODO: History -> Link Question ID to History ID

# TODO: PrintTable() compatibility with 'QustionHistory ' table
# TODO: ALter Question -> History Prints -> loadHstory method 1/2
# TODO: UI GENERAL IMPLEMETNATION -> Add Colors

class q:
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

def checkExisting(cur: sqlite3.Cursor, tableName: str, cond1: str, val1: int)-> bool:
    cmd = f"SELECT EXISTS(SELECT 1 FROM {tableName} WHERE {cond1} = (?) )"
    cur.execute(cmd, str(val1))
    result = cur.fetchone()
    return result[0]

# Adapters aConverters registered to sqlite3
# date -> string
def adapt_date(date_obj):
    return date_obj.isoformat()
# string -> date
def convert_date(date_text):
    return date.fromisoformat(date_text.decode())
sqlite3.register_adapter(date, adapt_date)
sqlite3.register_converter("DATE", convert_date)

def userInput():
    # TODO: Get user Input
    # NOTE: by default dateAttempted to today()
    # TODO: USER INPUT: "Did you attempt today? Y/N"
    #       if 'N', Prompt datetime input
    # NOTE: faking user inputs: completed, code, notes
    dateAttempted = date.today()
    print(f"Date Attempted:{dateAttempted}.")
    tempComp = True
    tempCode = "hello('World!')" #(optional)
    tempNotes = "this shit was hard!"

    return (tempComp, tempCode, dateAttempted, tempNotes)

def updateQHist(cur: sqlite3.Cursor, QID: int) -> None:
    # TODO: Update: Date Taken and/or Completed (if Applicable)

    tempComp, tempCode, dateAttempted, tempNotes = userInput()
    print(tempComp, tempCode, dateAttempted, tempNotes)


    cmd = f"INSERT INTO QuestionHistory VALUES(?, ?, ?, ?, ?, ?)"
    cur.execute(cmd, (None, QID, tempComp, tempCode, dateAttempted, tempNotes))


# TODO: change "Question_ID dynamically"
def addQuestion(cur: sqlite3.Cursor, tableName: str, question: q) -> None:

    if checkExisting(cur, tableName, "Question_ID", question.ID):
        print("Update Question History:")
        updateQHist(cur, question.ID)
        return
    
    # print("Adding Question to QuestionBank:")
    data = question.getData()

    placeholder = ', '.join(['?' for _ in range (len(data))])
    cmd = f"INSERT INTO {tableName} VALUES({placeholder})"
    cur.execute(cmd, data)

    updateQHist(cur, question.ID)


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

def printHelper(headers, widths) -> Tuple[str, str, str]:
    header_format = ""
    row_format = ""
    separator = "-" * (sum(widths) + len(widths) * 3 - 1)

    for i in range(len(headers)):
        header_format += f"{headers[i]:<{widths[i]}} | "
        row_format += f"{{:<{widths[i]}}} | "
    header_format = header_format[:-2]
    row_format = row_format[:-2]

    return (header_format, separator, row_format)


#TODO: Add colors
#TODO: Check "QuestionHistory" table compatability
def printTable(cur: sqlite3.Cursor, tableName: str) -> None:
    headers = []
    widths = []
    opt = ""

    if tableName == "QuestionBank":
        opt = "QBNK"
        headers = [" ROW ID", "QID", "NAME", "DIFFICULTY", "TYPE"]
        widths = [8,5,12,11,8]
    elif tableName == "QuestionHistory":
        opt = "QHIST"
        headers = [" ROW ID", "HID", "QID", "Completed", "CODE           ", "DATE", "NOTES"]
        widths = [8,5,5,11,6,12,7,]
    else:
        print("Invalid Table")

    header_format, separator, row_format = printHelper(headers, widths)
    cmd = f"SELECT rowid, * FROM {tableName}"
    cur.execute(cmd)
    items = cur.fetchall()

    print(f"\n{tableName}:\n")
    print(header_format)
    print(separator)

    #TODO:
    for item in items:
        if (opt == "QBNK"):
            print(row_format.format(item[0], item[1], item[2], item[3], item[4]))
        if (opt == "QHIST"):
            print(row_format.format(item[0], item[1], item[2], item[3], item[4], item[5], item[6]))



#TODO: Add formatting
'''
searchValue: Row Value ("TwoSum", "Hard", Question_ID)
attr: Col Name (QuestionID, Name, Complteted...)
'''
def printRow(cur: sqlite3.Cursor, tableName:str, searchValue , attr: str = "Question_ID") -> None:
    cmd = f"SELECT *  FROM {tableName} WHERE {attr} = ?"
    cur.execute(cmd, (searchValue,))

    row = cur.fetchone()
    if row:
        print(row)
    else:
        print("No row found with this specified criteria")


def printCol(cur: sqlite3.Cursor, tableName:str, id:int) -> None:
    cmd = f"SELECT "
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

#TODO: search for QID in QHIST and return LATES
def getLatestSubmission():
    pass
def getFullQuestionHistory():
    pass

#TODO: implement redoquestion tracking
# opt 1
# Redo create column in history (REDO-date) with DateCompleted + timedelta(wk2)
# Scheduler will execute one search of QHIST Daily, returning...
# The QID of where time.today() == redo.date
# opt 2
# Call getlastest submission() + timedelta(two weeks)
# Return value will be the date of submission + 2 weeks
# if return value == time.today() send notification
# TODO: 
# setup daily scheduler tha runs REDOQUESTION Tracking once a day

def main():
    connection = createDatabase()
    cursor = connection.cursor()

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
                "date_attempted DATE",
                "Notes TEXT",
                "FOREIGN KEY (Question_ID) REFERENCES QuestionBank(Question_ID)"
                ])

    printMasterSchema(cursor)

    q1= q(1, "TwoSum", "Easy", "Arrays")
    q2= q(2, "ThreeSum", "Medium", "LL")

    addQuestion(cursor, "QuestionBank", q1)
    addQuestion(cursor, "QuestionBank", q2)

    printTable(cursor, "QuestionBank")
    printTable(cursor, "QuestionHistory")

    printRow(cursor, "QuestionBank", 1)
    printRow(cursor, "QuestionBank", "TwoSum", "Name")

    connection.commit()
    connection.close()

if __name__ == "__main__":
    main()
