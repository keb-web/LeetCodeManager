from datetime import date, timedelta 

class LeetCodeQuestion:
    # Date, Difficulty, Type, SubType/Patterns + Notes, Complted(Y/N), Time (Optional), 
    # Reattempt History
    
    # TODO: Change diffuculty to const {} later (forget term lol)
    def __init__(self, QID: int, Name: str, Difficulty: str, Completed: bool , Duration: timedelta, Notes: str):
        self.retryDuration = timedelta(weeks=1)

        self.QID = QID
        self.Name = Name
        self.Difficulty = Difficulty
        self.Completed = Completed
        # Duration: amount of time to complete/attempt question
        self.Duration = Duration
        self.Notes = Notes
        # Date of attempt
        self.Date = date.today()

        if Completed:
            self.retryDate = date.today()
        else:
            self.retryDate = date.today() + self.retryDuration

        # print(self.Date)
        # print(self.retryDate)

    def updateRetryDuration(self, timeBlock):
        self.retryDuration = timeBlock

    # NOTE: Helper function, remove later
    def updateRetryDate(self, newDate):
        self.retryDate = newDate


    def __str__(self):
        return (
        """
        QID: %i
        Name: %s
        Difficulty: %s
        Compelted: %d
        Notes: %s
        Date: %s
        retryDate: %s
        """
        % (self.QID, self.Name, self.Difficulty, self.Completed, self.Notes, str(self.Date), str(self.retryDate))
        )

