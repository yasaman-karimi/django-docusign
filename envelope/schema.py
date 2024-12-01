from ninja import Schema
from pydantic import EmailStr


class Signer(Schema):
    name: str
    email: EmailStr


class CreateEnvelopeIn(Schema):
    first_party: Signer
    second_party: Signer
