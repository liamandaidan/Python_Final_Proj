from ast import Not
from datetime import datetime, timedelta
from fastapi import APIRouter, Body, Request, Response, HTTPException, status, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from typing import List
from jose import JWTError, jwt
from users import User, UserUpdate, UserAuth, Token, TokenData, Basic_User
from dotenv import dotenv_values
#import our config file
config = dotenv_values(".env")

#app is our authentication route
app = APIRouter()
#router is our user route
router = APIRouter()
#hashing, passwords and etc
passwordContext = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearerScheme = OAuth2PasswordBearer(tokenUrl="token")

USER_ROLES = {'A': "Admin",'U': "User", 'D': 'Disabled'}

def verifiyPassword(txt_pass: str, hashed_password: str)->bool:
    """Verifiy the integrety of the the password passed in.

    Args:
        txt_pass (str): plain txt password
        hashed_password (str): hashed password string

    Returns:
        bool: If valid password
    """
    return passwordContext.verify(txt_pass, hashed_password)

def hashPassword(password: str)-> str:
    """Hash text string

    Args:
        password (str): plain text to be hashed

    Returns:
        str: Hashed string
    """
    return passwordContext.hash(password)

def create_token(data: dict, expires: timedelta | None = None) -> str:
    """Create a bearer token with expiry time. Default time is 15 mins

    Args:
        data (dict): The user to encode into the token.
        expires (timedelta | None, optional): Time till expiry. Defaults to 15 mins.

    Returns:
        str: token
    """
    token = data.copy()#shallow copy user
    if expires:#if time is provided use config
        time = datetime.utcnow() + expires 
    else:#else default to 15 min
        time = datetime.utcnow() + timedelta(minutes=15)
    token.update({"exp": time}) #update our token with the new exp time
    return jwt.encode(token, config["SECRET_KEY"], algorithm=config["ALGORITHM"])#return an encoded str using our config file settings

def authenticate_user(request: Request, login: UserAuth = Body(...)):
    """Helper function used to valid a users login credentials. 

    Returns:
        dict|Boolean: Returns user on sucess. Else returns false if it does not exist
    """
    #find user by username
    if (user := request.app.database[config['DB_TABLE']].find_one({"username": login.username})) is not None:
        if verifiyPassword(login.password, user['password']): #check password
            return user  
        
    return False
async def get_current_user(request: Request, token: str = Depends(bearerScheme))-> dict:
    """Read the current user decoding the bearer token

    Args:
        request (Request): Dict passed in through method call
        token (str, optional): Bearer token. Defaults to Depends(bearerScheme).

    Raises:
        responseError: If username does not exist
        responseError: If jwttoken is invalid
        responseError: If user retrieve from jwt does not exist in db call

    Returns:
        dict: User returned
    """
    #Error Response data
    responseError = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate user's credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        #decode our jwt token payload using our env file configs
        decodedToken = jwt.decode(token, config["SECRET_KEY"], config["ALGORITHM"])
        username: str = decodedToken.get("sub")
        if username is None: #username does not exist, invalid jwt 
            raise responseError
        tokenData = TokenData(username=username) #Object enforcement
    except JWTError: 
        raise responseError
    #call our database to find user that exists under username
    user = request.app.database[config['DB_TABLE']].find_one({"username": tokenData.username})
    if user is None: #no user, throw error
        raise responseError
    return user


@app.post("/", response_description="Authenticate a user.", response_model=Token)
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends())->Token:
    """Login route for user authentication. Hash passwords, generate bearer token, validate.

    Args:
        request (Request): Passed in from request
        form_data (OAuth2PasswordRequestForm, optional): OAuth type passed in via export. Defaults to Depends().

    Raises:
        HTTPException: User provided wrong inputs

    Returns:
        Token: Enforced token schema
    """
    user = authenticate_user(request, form_data) #retrieve user from helper function
    if not user: #if user does not exist throw error. Wrong credentials
        raise HTTPException( status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="Incorrect username or password", 
                            headers={"WWW-Authenticate": "Bearer"})
    tokenExpires = timedelta(minutes=int(config["EXPIRE_TIME"])) #set expiry
    access_token = create_token(data={"sub": form_data.username}, expires=tokenExpires) #create token that will revoke acess
    return {"access_token": access_token, "token_type": "bearer"} #Token


@router.post("/", response_description="Create a new user", status_code=status.HTTP_201_CREATED, response_model=Basic_User)
async def create_user(request: Request, user: User = Body(...)) -> Basic_User:
    """Create a new user

    Args:
        request (Request): Passed in request
        user (User, optional): User schema enforcement. Defaults to Body(...).
    
    Returns:
        Basic_User: Basic details pretaining to user.
    """
    user.password = hashPassword(user.password) #hash user password
    user = jsonable_encoder(user)#encode our dict to a doc/json for mongo
    #if username already exists
    if request.app.database[config['DB_TABLE']].find_one({"username": user['username']}) is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Username {user['username']} taken, please try again")
    #always set new user role by default
    user['role'] = USER_ROLES["U"]
    new_user = request.app.database[config['DB_TABLE']].insert_one(user)#import data into db
    created_user = request.app.database[config['DB_TABLE']].find_one({ #retrieve newly created doc from mongo
        "_id": new_user.inserted_id
    })
    return created_user

@router.get("/", response_description="List all users", response_model=List[Basic_User])
async def all_users(request: Request)->List[Basic_User]:
    """Get all user from db return only basic user info

    Args:
        request (Request): Request passedin

    Returns:
        List[Basic_User]: List of all users. Only basic info
    """
    users = list(request.app.database[config['DB_TABLE']].find(limit=50))#restrict to 50 max for performance
    return users

@router.get("/{id}", response_description="Get a single user by id", response_model=User)
async def find_user(id: str, request: Request, current_user: User = Depends(get_current_user) )-> User:
    """Get a user by id. Will retrieve all information pretaining to their account

    Args:
        id (str): user id
        request (Request): The request passed in

    Raises:
        HTTPException: If user is not found

    Returns:
        User: All fields
    """
    if current_user['role'] != USER_ROLES["A"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User with role {current_user['role']} not permitted to perform this action.")
        
    if (user := request.app.database[config['DB_TABLE']].find_one({"_id": id})) is not None: #search db for first instance
        return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {id} not found")

@router.put("/", response_description="Update the logged in user", response_model=Basic_User)
async def update_user(request: Request, user: UserUpdate = Body(...), current_user: User = Depends(get_current_user)) -> Basic_User:
    """Update the logged in user checking their bearer token.

    Args:
        request (Request): The request passed in
        user (UserUpdate, optional): Fields requested to change. Defaults to Body(...).
        current_user (User, optional): Bearer token user. Defaults to Depends(get_current_user).

    Raises:
        HTTPException: If no fields are modified
        HTTPException: If user can not be found

    Returns:
        Basic_User: Basic user details returned
    """
    user = {key: val for key, val in user.dict().items() if val is not None} #check all key value pairs, return only matched 
    #if user requests to change their password
    if user.get('password') is not None: 
        user['password'] = hashPassword(user['password']) #hash
    if(len(user)) >= 1: #as long as user has more than one key value pairs
        output = request.app.database[config['DB_TABLE']].update_one( #send update to db
            {"_id": current_user['_id']}, {"$set": user}
        )
    if output.modified_count == 0: #if no fields modified
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {current_user['_id']} not found")
    
    if( existing_user := request.app.database[config['DB_TABLE']].find_one({"_id": current_user['_id']})) is not None: #if user is not found
        return existing_user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {current_user['_id']} not found")

@router.delete("/{id}", response_description="Delete a user", response_class=ORJSONResponse )
async def delete_user(id: str, request: Request, response: Response, current_user = Depends(get_current_user)) ->ORJSONResponse:
    """Delete a user

    Args:
        id (str): User id
        request (Request): request passed in
        response (Response): response passed in

    Raises:
        HTTPException: If user is not found

    Returns:
        ORJSONResponse: custom json response
    """
    if current_user['role'] != USER_ROLES["A"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User with role {current_user['role']} not permitted to perform this action.")
    
    delete_user = request.app.database[config['DB_TABLE']].delete_one({"_id": id})#delete user at id
    
    if delete_user.deleted_count == 1: #if deleted user
        return ORJSONResponse({"Message:": "User Deleted."})
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {id} not found")

@router.get("/me/", response_model=Basic_User, description="Check the bearer token and return current logged in user details.")
async def read_users_me(request: Request, current_user: User = Depends(get_current_user))->Basic_User:
    """Check bearer token, return current logged in user details

    Args:
        request (Request): Request passed in
        current_user (User, optional): User params. Defaults to Depends(get_current_user).

    Returns:
        Basic_User: Basic user info
    """
    return current_user
