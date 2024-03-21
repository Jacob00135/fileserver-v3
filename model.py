class User(object):

    def __init__(self, user_name, user_password_hash):
        pass
    
    def create_user(self, user_name, user_password):
        pass

    @staticmethod
    def query_by_id(user_id):
        return 0

    @staticmethod
    def query_by_username(user_name):
        return 0

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return self.is_active

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.user_id)
