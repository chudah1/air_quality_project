from flask import Flask, session, render_template, request, redirect

import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore




app = Flask(__name__)


config = {
"apiKey": "AIzaSyDJ8_IAWiRwQQ7c2fYqV7TBiu92AdH0yq0",
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

app.secret_key = "secret_key"

#initialize the firestore database
cred = credentials.Certificate("airquality.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
users= db.collection("users")

@app.route('/air_quality/register', methods=['GET', 'POST'])
def create_account():
    if (request.method == 'POST'):
            email = request.form.get('email')
            password = request.form.get('password')
            auth.create_user_with_email_and_password(email, password)
            users.add({"email":email})
            return "created user"
    return "Register account"

@app.route("/air_quality/login", methods = ["GET", "POST"])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session['user'] = email
        except:
            return 'Wrong email or password'
    return "login Form"

@app.route("/air_quality/logout")
def logout():
    session.pop('user')
    return redirect('/air_quality/login')

if __name__ == "__main__":
    app.run(debug=True)