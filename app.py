from flask import Flask, session, render_template, request, redirect

import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv
from utils import *


load_dotenv() 



app = Flask(__name__, static_url_path='/static')


config = {
"apiKey": os.getenv('API_KEY'),
"authDomain": "airquality-d611e.firebaseapp.com",
"projectId": "airquality-d611e",
"storageBucket": "airquality-d611e.appspot.com",
"messagingSenderId": "636721957126",
"appId": "1:636721957126:web:02ad2cf7c222b4b5013687",
"measurementId": "G-29Z39BMNP4",
"databaseURL":""
}

firebase = pyrebase.initialize_app(config)

auth = firebase.auth()

app.secret_key = os.getenv('SECRET_KEY')

firebase_key = os.getenv("FIREBASE_KEY")

#initialize the firestore database
cred = credentials.Certificate(
    { 
"type": "service_account",
  "project_id": "airquality-d611e",
  "private_key_id": os.getenv('PRIVATE_KEY'),
  "private_key": os.getenv('FIREBASE_KEY'),
  "client_email": "firebase-adminsdk-yjju3@airquality-d611e.iam.gserviceaccount.com",
  "client_id": "112749579766246350632",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-yjju3%40airquality-d611e.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

)
firebase_admin.initialize_app(cred)
db = firestore.client()
users= db.collection("users")

@app.route('/air_quality/register', methods=['GET', 'POST'])
def register():
    if (request.method == 'POST'):
            email = request.form.get('email')
            password = request.form.get('password')
            username = request.form.get('username')
            auth.create_user_with_email_and_password(email, password)
            users.add({"email":email, "username":username})
            return "created user"
    return render_template('authentication-register.html')

@app.route("/air_quality/login", methods = ["GET", "POST"])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session['user'] = email
            return "Login"
        except:
            return 'Wrong email or password'
    return render_template('authentication-login.html')

@app.route("/air_quality/logout")
def logout():
    session.pop('user')
    return redirect('/air_quality/login')

def create_user_and_verify_email(email, password):
    try:
        user = auth.create_user_with_email_and_password(email, password)
        auth.send_email_verification(user['idToken'])
        return True
    except Exception as e:
        print("Error creating user and verifying email:", e)
        return False
    
@app.route("/air_quality/threshold/<user_id>", methods = ["GET", "POST"])
def threshold(user_id):
    if request.method == "POST":
        location = request.form.get("location")
        threshold = request.form.get("threshold")
        thresholds = {"location":location, "threshold":threshold}
        users.doc(user_id).update({"thresholds": firestore.ArrayUnion([thresholds])})

if __name__ == "__main__":
    app.run(debug=True)