from os import walk
import sqlite3
from sqlite3.dbapi2 import Row
from typing import List
from datetime import timedelta, datetime

# TODO: time attributes and loading history
# TODO: History -> update history with new submission
# TODO: History -> Link Question ID to History ID
# TODO: Prettier Table output formatting


class q:
    # TODO: add time attributes
    def __init__(self, ID: int, Name: str, Difficulty: str, Type: str, Date: datetime = None) -> None:
        self.ID = ID
        self.Name = Name
        self.Difficulty = Difficulty
        self.Type = Type
        self.Date = Date if Date is not None else datetime.today()

    # TODO: Update getters to return AttemptDate
    def getData(self) -> tuple:
        return (self.ID, self.Name, self.Difficulty, self.Type)

    def __str__(self):
        return (f"{self.ID}, {self.Name}, {self.Difficulty}, {self.Type}")


def createDatabase():
    con = sqlite3.connect("questions.db")
    return con


def createTable(cur: sqlite3.Cursor, tableName : str, attr: List[str]) -> None:
    columns = ', '.join(attr)
    print("__Creating table__")
    # print("__Creating table with:__")
    # print(columns)
    cmd = f"CREATE TABLE IF NOT EXISTS {tableName}({columns})"
    cur.execute(cmd)


# TODO: Debug 'checkExisting' due to change in datatype (val1 -> string to Int)
def checkExisting(cur: sqlite3.Cursor, tableName: str, cond1: str, cond2: str, val1: int, val2:str)-> bool:
    print("__CHECKEXISTING__")
    # NOTE: check AND instead
    cmd = f"SELECT EXISTS(SELECT 1 FROM {tableName} WHERE {cond1} = (?) OR {cond2} = (?))"
    cur.execute(cmd, (val1, val2))
    result = cur.fetchone()
    return result[0]
    

def updateRow(RowAttr):
    #TODO: Update: Date Taken and/or Completed (if Applicable)

    print(RowAttr)
    pass

def addQuestion(cur: sqlite3.Cursor, tableName: str, question: q) -> None:

    if checkExisting(cur, tableName, "ID", "Name", question.ID, question.Name):
        print("Value Exists.. Update Row")
        # TODO: add code to update existing question
        updateRow("Name")
        return
    
    # Add Question as Row to Table
    data = question.getData()
    placeholder = ', '.join(['?' for _ in range (len(data))])
    cmd = f"INSERT INTO {tableName} VALUES({placeholder})"
    cur.execute(cmd, data)

    # verify insertion
    cmd = f"SELECT Name from {tableName}"
    res = cur.execute(cmd)
    print(res.fetchall())

# TODO: 
# IN OBSIDIAN NOTES
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

def alterQuestion():
    pass



def printMasterSchema(cur: sqlite3.Cursor, attr: str = "name")-> None:
    """
    printMasterSchema prints all table [attr] contained in the Schema Table
    :param cur: Database Cursor
    :param attr: By default is name. The attribute of each table that is printed
    """
    cmd = f"SELECT {attr} FROM sqlite_master"
    res = cur.execute(cmd)
    print(res.fetchall())


def printTableColumns(cur: sqlite3.Cursor ):
    pass


def printTable(cur: sqlite3.Cursor, tableName: str) -> None:
    print("__printing table__")

    cur.execute("SELECT rowid, * FROM LCQ")
    items = cur.fetchall()
    for item in items:
        # print(rowid)
        print(item)
        # print(rowid + ": " + item[0] + " " + item[1] + " " + item[2] + " " + item[3])

def printRow():
    pass

def printAttr():
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

    # testQuestion = q(ID, Name, Difficulty, QuestionType)
    # dupe = q(ID, Name, Difficulty, QuestionType)
    # testQuestion2 = q("1", "THREESUM", "Medium", "Arrays")
    # testQuestionRemove = q("2", "TODELETE", "HARD", "TREES")

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
                "Attempt_Number INTEGER",
                "Code TEXT",
                "date_attempted DATETIME",
                "Notes TEXT",
                "FOREIGN KEY (Question_ID) REFERENCES QuestionBank(Question_ID)"
                ])

    printMasterSchema(cursor)

    # addQuestion(cursor, TableName, testQuestion)
    # addQuestion(cursor, TableName, testQuestion2)
    # addQuestion(cursor, TableName, dupe)
    # addQuestion(cursor, TableName, testQuestionRemove)

    # printTable(cursor, TableName)

    connection.commit()
    connection.close()

if __name__ == "__main__":
    main()
