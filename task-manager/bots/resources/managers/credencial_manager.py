class CredencialManager:
    def __init__(self, bot: object) -> None:
        self.bot = bot

    def load_credenciais(self, config: dict) -> None:
        self._username = config["username"]
        self._password = config["password"]

    @property
    def username(self) -> str:
        return self._username

    @property
    def password(self) -> str:
        return self._password
