class NotificationMessage:
    def __init__(self, body, subject):
        self.body = body
        self.subject = subject

    def data(self):
        return {"body": self.body, "subject": self.subject}
