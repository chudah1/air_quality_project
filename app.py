from flask import Flask, session, render_template, request, redirect, url_for
import atexit
import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

from utils import *
from apscheduler.schedulers.background import BackgroundScheduler


load_dotenv() 



app = Flask(__name__, static_url_path='/static')


def check_thresholds_and_alert():
    users = db.collection("users").get()
    for user in users:
        user_data = user.to_dict()
        if "thresholds" not in user_data:
            continue
        thresholds = user_data["thresholds"]
        email = user_data["email"]
        for threshold in thresholds:
            location = threshold["location"]
            threshold_value = threshold["threshold"]
            air_quality_data = fetch_air_quality(location)
            if air_quality_data > threshold_value:
                send_emails(email, location, air_quality_data)

scheduler = BackgroundScheduler()


scheduler.start()


scheduler.add_job(check_thresholds_and_alert, trigger="interval", hours=48)




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
  "private_key": firebase_key,
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


@app.route('/air_quality/home')
def home():
    # Check if the user is logged in
    if 'user' in session:
        return render_template('index.html')
    else:
        return redirect(url_for('login'))


@app.route('/air_quality/register', methods=['GET', 'POST'])
def register():
    if (request.method == 'POST'):
            email = request.form.get('email')
            password = request.form.get('password')
            username = request.form.get('username')
            user = auth.create_user_with_email_and_password(email, password)
            doc_ref = users.add({"email":email, "username":username})
            doc_id = doc_ref[1].id
            session['user'] = user
            session['doc_id'] = doc_id
            return redirect(url_for('home'))
    return render_template('authentication-register.html')


@app.route("/air_quality/login", methods = ["GET", "POST"])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session['user'] = email
            return render_template('index.html')
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
        users.document(user_id).update({"thresholds": firestore.ArrayUnion([thresholds])})

        return "Successfully created"
    return "Could not set threshold"

if __name__ == "__main__":
    app.run(debug=True)