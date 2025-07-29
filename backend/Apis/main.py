from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.Apis.RecipeRequest import router as recipe_router
from backend.Apis.auth import router as auth_router


app = FastAPI()

#CORS control: meaning we cant have outside applications hitting our fastapi, without us saying this application is allowed to make calls to our endpoints, protects from outside users
app.add_middleware(
    CORSMiddleware,
    #allow all types requsts if its from our frontend
    allow_origins=["http://localhost:5173"],  # frontend origin, when deployed change to production server name
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#include routers from the recipe request module
app.include_router(recipe_router)
app.include_router(auth_router)