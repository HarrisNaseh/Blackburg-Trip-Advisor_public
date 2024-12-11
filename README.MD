# VT Trip Advisor
## Getting started

We are using python with Flask to host our backend. To make things go smoothly we will use a python virtual environment.

## VENV SETUP:
Navigate to the server directory
create venv by running ```python -m venv venv```
Run ```source venv/Scripts/activate```
Also make sure to be in the venv python interpreter by clicking your version in the bottom right corner and making sure the path is set to ```venv/Scripts/python```
You should now be in venv, to install all dependencies, run ```pip install -r requirements.txt```
Make sure to update requirements.txt if intalling new dependencies by running ```pip freeze > requirements.txt```

## Basics of Flask
This is a good resource to get a grasp of Flask: https://www.youtube.com/watch?v=MwZwr5Tvyxo&t=660s&ab_channel=CoreySchafer
I watched the first 4 parts

## Running the Flask app
Make sure you in your python environment and run this command: ```python run.py``` this spins up flask server and will print out a url for you to follow. You can enter that url into a browser to see
the index.html file. 

## Git commands
To add files that you want to push to the repo you need to run ```git add {yourfilename}``` or if you want to add everything that you have worked on you can do ```git add .```. Now you need to commit your changes. Run ``` git commit -m "your commit message here"```. Finally you need to push your changes: ```git push  ```
