from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from dotenv import dotenv_values
from pymongo import MongoClient
from userRoute import router as user_router
from userRoute import app as cool

config = dotenv_values(".env")

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def root():
    """Upon loading server user will be navigated here.

    Returns:
        _type_: _description_
    """
    #return html resp
    return """
    <html>
        <head>
            <title>Python final proj</title>
        </head>
        <body>
            <h1>Python final project.</h1>
            <h3>By Liam McLaughlin</h3>
            <p>
            Please navigate to the docs for a user interface unless you intend to use a third party such as thunderclient/postman
            </p>
            <a href="/docs">Navigate to swagger GUI here..</a>
        </body>
    </html>  
    """

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