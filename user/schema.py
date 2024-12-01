from ninja import Schema


class UserIn(Schema):
    username: str
    password: str


class UserOut(Schema):
    id: int
    username: str


class ErrorMessage(Schema):
    message: str
