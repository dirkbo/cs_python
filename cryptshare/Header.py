class Header:
    general = {
        "X-CS-MajorApiVersion": "1",
        "X-CS-MinimumMinorApiVersion": "8",
        "X-CS-ProductKey": "api.rest",
    }

    def set_client_id(self, id):
        self.general.update({"X-CS-ClientId": id})

    def set_verification(self, token):
        self.general.update({"X-CS-VerificationToken": token})

    def set_origin(self, origin):
        self.general.update(({"Origin": origin}))

    def other_header(self, other):
        new_header = self.general.copy()
        new_header.update(other)
        return new_header
