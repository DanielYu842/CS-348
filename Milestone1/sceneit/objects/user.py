class User:
    @staticmethod
    def user_attrs_soft_check(user_attrs):
        return all(value for value in user_attrs.values())

    def __init__(self, user_attrs):
        self.user_id = int(user_attrs['user_id'])
        self.username = user_attrs['username']
        self.email = user_attrs['email']
        self.password_hash = user_attrs['password_hash']
        self.created_at = user_attrs['created_at']
        self.updated_at = user_attrs.get('updated_at', None)  # Default to None if not provided
