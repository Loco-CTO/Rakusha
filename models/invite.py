import uuid

from database import db_handler


class Invite:
    def __init__(self, code, used=False):
        self.code = code
        self.used = used

    @staticmethod
    def create_invite():
        code = str(uuid.uuid4())
        invite = Invite(code)
        invite.save()
        return invite

    @staticmethod
    def get_by_code(code):
        query = "SELECT * FROM invites WHERE code = ?"
        result = db_handler.execute(query, (code,))
        if result:
            return Invite(*result[0])
        return None

    @staticmethod
    def get_all_invites():
        query = "SELECT * FROM invites"
        result = db_handler.execute(query)
        return [Invite(*row) for row in result] if result else []

    def save(self):
        query = "INSERT INTO invites (code, used) VALUES (?, ?)"
        db_handler.execute(query, (self.code, self.used))

    def mark_as_used(self):
        query = "UPDATE invites SET used = ? WHERE code = ?"
        db_handler.execute(query, (True, self.code))

    @staticmethod
    def delete_invite(code):
        query = "DELETE FROM invites WHERE code = ?"
        db_handler.execute(query, (code,))
