class User:
    """
    Represents a user in the system.

    Attributes:
        id (int): The unique identifier of the user.
        username (str): The username of the user.
        email (str): The user's email address.
        password (str): The user's password (should be stored securely).
        role (str): The role of the user (e.g., admin, customer).
    """

    def __init__(self, id: int, username: str, email: str, password: str, role: str):
        """
        Initializes a new User instance.

        Args:
            id (int): The unique identifier of the user.
            username (str): The username of the user.
            email (str): The user's email address.
            password (str): The user's password.
            role (str): The user's role in the system.
        """

        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.role = role


