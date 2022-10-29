# Python_Final_Proj
## Introduction  
The purpose of my project is to illustrate restful api services around user accounts. This will cover some of the basic functions, along with admin functions.
In this project I used mongoDB for the database functions, feel free to connect using all the information within the .env file. 
## Quick demo  
For a video demonstration and quick run through of functionality:   
https://youtu.be/DoxDfyTxra4   
## Configuration
To get started, all config used for the app is located within .env. This will be provided to you along with assignment submission. 

To start a local server I used python package uvicorn.  
`python -m uvicorn main:app --reload`
![image](https://user-images.githubusercontent.com/84680661/198737967-28f7c87a-7ddb-45c2-99f0-f1b90c6317a5.png)  
Navigate to the URL provided.  
Once there append /docs to your url. You will come to the FastApi Swagger interface. 
![image](https://user-images.githubusercontent.com/84680661/198738504-6a563e8f-b8c9-4892-9291-7f46a109553f.png)
