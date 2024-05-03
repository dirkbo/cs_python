class Sender:
    def __init__(self, name, phone):
        self.name = name
        self.phone = phone

    def data(self):
        return {"name": self.name, "phone": self.phone}
