import sys
sys.path.insert(0, './problem_domain')
from database import connect

def display():
    print('Welcome to the password manager! Would you like to create an account(1) or log in(2)?')
    userInput = int(input("Please enter your choice as an integer: "))
    match userInput:
        case 1:
            createAcc()
        case 2:
            logIn()
    pass

def logIn():
    pass

def createAcc():
    print(connect())
    pass