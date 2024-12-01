from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from ninja import Router

from .schema import ErrorMessage, UserIn, UserOut

router = Router()


@router.post("/", auth=None, response={200: UserOut, (422, 400): ErrorMessage})
def user_register(request, user_info: UserIn):
    try:
        user = User.objects.create_user(
            username=user_info.username, password=user_info.password
        )
        return 200, UserOut(id=user.id, username=user.username)
    except IntegrityError:
        return 422, ErrorMessage(message="username already exists.")


@router.post("/login", auth=None, response={200: UserOut, (402, 401): ErrorMessage})
def user_login(request, user_info: UserIn):

    user = authenticate(username=user_info.username, password=user_info.password)
    login(request, user)
    return 200, UserOut(id=user.id, username=user.username)
