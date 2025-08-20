class MySQL():
    server: str
    port: int
    user: str
    password: str
    data_base: str
    url: str

    def __init__(
            self, 
            server: str, 
            port: int, 
            user: str, 
            password: str, 
            data_base: str, 
            url: str,
    ):
        self.server = server
        self.port = port
        self.user = user
        self.password = password
        self.data_base = data_base
        self.url = url