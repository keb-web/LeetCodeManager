TODO: 
# use SQLlite library to save object data
# use schedule.py to automate notifictions 
# create daily notifications through discord bot
# create basic CLI (will be updated to webbrowser in future)
# Convert Project to TS

import schedule
import discord

from datetime import date,  timedelta
from Question import LeetCodeQuestion 
from data import QuestionTable


def UI_Manager():
    displayFlag = True
    while displayFlag:
        selection = input(
        """
        (1) Add a Question
        (2) Manually Check Retries
        (3) Update Question
        (x) Close Prompt
        """
        ).strip()

        if selection not in ["1", "2", "x"]:
            print("Not an option please try again")
            continue

        qt = QuestionTable()

        q  = LeetCodeQuestion(1, "TwoSum", "Easy", False, timedelta(minutes=30), "testing..." )
        qt.addQuestion(q)

        if selection == "1":
            questionID = int(input("QID? "))
            questionName = input("Name? ").strip()
            questionDifficulty = input("Difficulty (E/M/H)? ").strip()
            solved = input("Solved (Y/N)? ").strip().upper()
            solved = True if solved == "Y" else False
            # NOTE: change this back after testing
            # duration = input("How long did it take (-1 for idk)")
            # notes = input("Any notes?")
            notes = "it was hard"
            duration = timedelta(minutes=30)
            question = LeetCodeQuestion(questionID, questionName, questionDifficulty, solved, duration, notes )
            qt.addQuestion(question)

        elif selection == "2":
            inputDate = input("Input 'All', a Date (MM/DD/YYYY), or leave empty for today")
            if len(inputDate) > 10:
                print("Invalid input, please try again")
                continue

            if inputDate == "":
                print("Returning today's")
                qt.printTODO(qt.getTODO(date.today()))
            elif inputDate.upper() == "ALL":
                qt.printUpcoming()
            else:
                m, d, y= inputDate.split('/')
                userDate = date(int(y), int(m), int(d))
                qt.printTODO(qt.getTODO(userDate))

        elif selection == "3":
            print("Updating retry")

        if selection == "x":
            displayFlag = False

        print("Done with UI....")
        qt.print_dict_QID()

        break
    return
            

# Schedule.py
# Check upcoming questions every day
# If there is one due on current day, send notification
def dailyJob(QuestionBank):
    pass

def sendNotification():
    pass

#TODO: Daily questions quizzing different patterns
#TODO: Daily checkoff for completed daily question


def testFunction():
    # WARNING: remove later
    currentDay = date.today()
    timeBlock = timedelta(weeks=2, days=1)

    # today + two weeks from now
    x = currentDay + timeBlock

    qt_test = QuestionTable()
    q  = LeetCodeQuestion(1, "TwoSum", "Easy", False, timedelta(minutes=30), "testing..." )
    q2  = LeetCodeQuestion(2, "ThreeSum", "Medium", False, timedelta(minutes=30), "testing..." )
    q3  = LeetCodeQuestion(3, "FourSum", "", False, timedelta(minutes=30), "testing..." )

    # updating date for testing
    q2.updateRetryDate(x)

    qt_test.addQuestion(q2)
    qt_test.addQuestion(q3)
    qt_test.addQuestion(q)
    # Test ignore print Upcoming
    # testDate = date(2024, 5, 29)
    # print(testDate)
    # qt_test.printUpcoming(testDate)

    # returns date 2024-06-06
    # print(qt_test.getTODO(x))
    # finds questions with that date
    # qt_test.printTODO(qt_test.getTODO(x))

def main():
    UI_Manager()

if __name__ ==  "__main__":
    main()

