#ALI server file
from bottle import route, get, post 
from bottle import run, debug
from bottle import request, response, redirect, template
from bottle import default_app
from bottle import static_file
import json
import random
import string
import hashlib
import os
import codecs
import dataset


#!!! please have username as 'username' inside mySql datbase. it will be easier in the future
#login page functionality
@get("/")
def getloginPage():
    return template("login")

@post("/")
def postloginPage():
    session = getSession(request)
    # this will grap user input from html page
    username = request.forms.get('username') 
    password = request.forms.get('password')

    user = getUser(username)
    #!!we need to add a pop up if user credentials is wrong. Because we can not redirect to signup page
    #bootstrap has some cool alert messages 
    if not user:
        return redirect('/') #if not found will redirect user back to login page
    if 'credentials' not in user:
        return redirect('/')
    if not verifyPassword(password, user['credentials']):
        return redirect('/') #if password is wrong will redirect to login page
    session['username'] = username #gives user name to session
    saveSession(response, session) #saves the session
    return redirect('/home') #will redirect to home page with the user being logged in 


#ADMIN create account functionality
#code for create an account will be added here

@route("/home")
def homePage():
    return template("home")

@get("/signup") #returns sign up page 
def getSignUp():
    return template("signup")

@post("/signup")
def postSignUp():
    session = getSession(request) #get session
    companyKey = request.form.get('companyKey')
    username = request.forms.get('username') #get username form page
    password = request.forms.get('password') #get password from page
    passwordRepeat = request.forms.get('password_again') #get password from page
    if password != passwordRepeat: #makes sure the double password input is the same
        saveSession(response, session) 
        return redirect('signup')    #will redirct to home page if not the same
    ##need to check key before 
    saveUser(username, { #saves user after signup
        'username':username,
        'credentials':generateCredentials(password),
        'companyKey' :companyKey #change to company name
    })
    session['username'] = username #sets session user name to the new users name
    saveSession(response, session)
    return redirect('/')

#---------------session functions------------------------
def getSession(request):
    
    def newSession(): #creates new session dic
        sessionId = newSessionId()
        s = { #creating dic
            "session_id" : sessionId,
            "username" : ''
        }
        return s #returning data

    sessionId = request.get_cookie("session_id", default=None) #asking for browser given data
    if sessionId == None:
        s = newSession() #if none found create new
    else: # if found, get it 
        try:
            s= read(sessionId) 
        except: # exception for proctection
            s = newSession()
    return s #return session 

#saving session 
def saveSession(response, session):
    write(session['session_id'], session) #write through json
    response.set_cookie("session_id", session['session_id'], path="/") # sets session 

#uses token function to get new session ID
def newSessionId():
    return createToken()

#create token for session ID
def createToken(k=32):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=k)) #creates random string





#---------------------json file functions---------------------------------------
def write(key, data):
    assert type(data) is dict
    with open(f"data/session.{key}.json", "w") as f: #writes to json file
        json.dump(data,f) #dumb for write
    return

def read(key):
    with open(f"data/session.{key}.json", "r") as f: #reads from json file
        data = json.load(f) #load for read
    assert type(data) is dict #make sure it is a dict data type
    return data

def getUser(name):
    try:
        with open(f"data/user.{name}.json", "r") as f: #reads from json file to find username
            data = json.load(f) #load for read
        assert type(data) is dict #makes sure is dic data ype
        return data
    except:
        return None

def saveUser(name, data):
    assert type(data) is dict #make sure it is a dict data type
    with open(f"data/user.{name}.json", "w") as f: #writes data to json file 
        json.dump(data,f) #dump for write
    return







#------------------------Credential functions---------------------
#function for hashing process
def bytesToString(byte):
    string = str(codecs.encode(byte,"hex"),"utf-8") #using utf-8 to change bytes to a string
    assert type(string) is str #making sure its a string
    return string
#function for hashing process
def stringToBytes(string):
    byte = codecs.decode(bytes(string,"utf-8"),"hex") #changing from string to bytes
    assert type(byte) is bytes #making sure its bytes
    return byte

#The hashing function 
def generateCredentials(Userpassword):
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac(
        'sha256', # The hash digest algorithm for HMAC
        Userpassword.encode('utf-8'), #Makes password byes
        salt, # Provide the salt
        100000 # It is recommended to use at least 100,000 iterations of SHA-256 
        )
    return {  #returns hash
        'salt':bytesToString(salt), 
        'key' :bytesToString(key),
    }

#passwords need to be verified. We need to hash and compare to see if its verifiable 
def verifyPassword(Userpassword, Usercredentials):
    salt = stringToBytes(Usercredentials['salt']) #get salt
    key  = stringToBytes(Usercredentials['key'])  #get key
    
    newKey = hashlib.pbkdf2_hmac( #process to hash the password to compare
        'sha256', # The hash digest algorithm for HMAC
        Userpassword.encode('utf-8'), # Convert the password to bytes
        salt, # Provide the salt
        100000 # It is recommended to use at least 100,000 iterations of SHA-256 
        )
    return newKey == key #returns bool to see if they match


#def checkCompanyKey():
    #need function to verify companies keys



#for images on page
@route("/static/png/<filename:re:.*\.png>")
@route("/image/<filename:re:.*\.png>")
def get_image(filename):
    return static_file(filename=filename, root="static/images", mimetype="image/png")

@route("/static/<filename:path>")
def get_static(filename):
    return static_file(filename=filename, root="static")

if __name__ == "__main__":
    debug(True)
    run(host="localhost", port=8080)
else:
    application = default_app()