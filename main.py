from fastapi import FastAPI
from dotenv import dotenv_values
from pymongo import MongoClient
from userRoute import router as user_router
from userRoute import app as cool

config = dotenv_values(".env")

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "To begin navigate to /docs"}

@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient(config["ATLAS_URI"])
    app.database = app.mongodb_client[config["DB_NAME"]]
    print("Connected to the MongoDB database!")

@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()
    
app.include_router(user_router, tags=["users"], prefix="/user")
app.include_router(cool, tags=["token"], prefix="/token")