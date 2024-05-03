class SecurityMode:
    def __init__(self, password="", mode="GENERATED"):
        if mode == "NONE":
            self.config = {"passwordMode": "NONE"}
        elif mode == "GENERATED" and password == "":
            self.config = {"passwordMode": "GENERATED"}
        elif mode == "GENERATED":
            self.config = {"passwordMode": "GENERATED", "password": password}
        elif mode == "MANUAL":
            self.config = {"passwordMode": "MANUAL", "password": password}
        self.name = "ONE_TIME_PASSWORD"

    def data(self):
        return {"name": self.name, "config": self.config}
