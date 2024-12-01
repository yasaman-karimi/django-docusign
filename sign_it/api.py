from ninja import NinjaAPI
from ninja.security import HttpBasicAuth, SessionAuth

from envelope.api import router as envelope_router
from user.api import router as user_router

api = NinjaAPI(auth=(SessionAuth(csrf=False),))

api.add_router("/user/", user_router)
api.add_router("/envelope/", envelope_router)
