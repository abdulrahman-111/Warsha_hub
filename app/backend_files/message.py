# In your backend files (where you have USER, POST classes)
class Msg:
    def __init__(self):
        self.msg_id = 0
        self.sender_id = 0
        self.receiver_id = 0
        self.date = ""
        self.content = ""

    def set_msg_id(self, msg_id):
        self.msg_id = msg_id

    def set_sender_id(self, sender_id):
        self.sender_id = sender_id

    def set_receiver_id(self, receiver_id):
        self.receiver_id = receiver_id

    def set_date(self, date):
        self.date = date

    def set_content(self, content):
        self.content = content