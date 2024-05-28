from datetime import date
import enum

# TODO: Quick easy storage method, will update to database after functionality

class QuestionTable:
    def __init__(self):
        #duration of time passed until a question is retried
        self.questions = []

        # NOTE: for future filtered functionality
        # might be unessessary....
        self.questionID = {}
        self.questionName = {}

        # dict[DateComplted] = q
        # makes it easier to search by dates
        self.questionRDate= {}

    def addQuestion(self, q):
        print("adding Question: ", q.Name)
        if q.QID in self.questionID:
            print("Question '%s' already logged" % (q.Name))
            return

        self.questions.append(q)
        self.questionID[q.QID] = q
        self.questionName[q.Name] = q
        if q.retryDate not in self.questionRDate:
            self.questionRDate[q.retryDate] = [q]
        else:
            self.questionRDate[q.retryDate].append(q)

    def deleteQuestion(self, q):
        self.questions.remove(q)
        del self.questionID[q.QID]
        del self.questionName[q.Name]

    def updateCompletion(self, q, status):
        self.questionID[q.QID].Completed = status
        self.questionName[q.Name].Completed = status
        for i, val in enumerate(self.questions):
            if val == q:
                self.questions[i].Completed = status

    def getQuestions(self):
        return sorted(self.questions, key= lambda question: question.retryDate)

    def getTODO(self, searchDate):
        print("searching for, ", searchDate)
        if searchDate in self.questionRDate:
            return self.questionRDate[searchDate]
        print("nothing found")
        return 

    #TODO: implement in future
    # def getHistory(self):
    #     pass
    #TODO: implement in future
    # def searchQID(self):
    #     pass

    # HELPER FUNCTIONS
    def printTODO(self, searchDate):
        print("_____ TODOS ... ____")
        for val in searchDate:
            print(val)

    # Prints entire list of upcoming questions in order
    def printUpcoming(self, ignoreDate = date.today()):
        print("_____ Upcoming Questions ... ____")
        print("Ignore Date: ", ignoreDate)
        for i in self.getUpcoming():
            if i.retryDate == ignoreDate:
                continue
            print(i)

    # Filter by Question ID Number
    def print_dict_QID(self):
        for key, value in self.questionID.items():
            print( key, value)

    # Filter by Question Name
    def print_dict_Name(self):
        for key, value in self.questionName.items():
            print( key, value)

    # Print entire question bank
    def print_questionArr(self):
        print("printing arr")
        for val in self.questions:
            print(val)

    # Execute all Helper Printer Functions
    def test_printALL(self):
        print("PRINTING ALL: ")
        self.print_dict_QID()
        self.print_dict_Name()
        self.print_questionArr()
