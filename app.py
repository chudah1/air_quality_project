from flask import Flask, session, render_template, request, redirect
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


scheduler.add_job(check_thresholds_and_alert, trigger="interval", minutes=1)




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
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDYXWDcbKTbX5P/\nrncxk7f47GmzBWwvKeQUzmeHsrxQ39piRBf3kTfcp/MN9tpmkn8wtsF030u7m00S\nDk99SsRJTc480hSHsiCwjyIAKpD49IrBOUJugLOzXI2her12CV7wtLUfKylbKrYk\nPXHEXQZAUCAnK/oIyi7Nd1GXPF/vTEjUpPyc1xW86qkuQ59et+USWlZR7XOWtlY1\nKIaWKC949UDsjO2RRfQjNeMvnYDfBsKASOwFUDfiJ3HLHk4bxX3s939u96DPJyhI\nBfEzzCJWCreS+Mu33UPXZKvU3CLdsLQ7mraETP0fJBSmfubVeLx8lkLMWVSymvwZ\nW6Uj47qrAgMBAAECggEAI/30nPZdvjh6EDBfl5mxIvGA68zdIENhs6xaQJKVDQcP\n9wTIz+ASYNx3bD1CO4nnKp1cNSroGD9PZM+InZkQaflNc4Sm8aPKGFTXHRv3ndJg\nOqBh0qwKOK4OyWv3lGkeqAAHmTW+3XGPdxvZjwbCgXRSxPFl2Ix5mKhepD/g3ZeO\negqvIor57mNtDMSyYi1i38NupCnwUNoEABud/eQgJgzpzzDluhLaHKVPrFIuVCS7\nd94g5GUJ+pDaev4BdZlBKXQJCrpDT+carISARYv3z/qR9T84ezq47al82FBZ3vkU\ndWRx8U3WtSG8GZhiQFB09dfwK57Px2sigF5qUaY+cQKBgQD/+tNgOlNWrT3B5ceG\ntwj3i2t3I+4xagFFRdpVeACODT6gURtcabcEN36oKkbIO9Itx5t2tvSg3Smqi25z\nq1NcdvoH75wroUDl2rRIb44QTPJks2gXHtJByDUcTo5SvKMLdq94f9XCMJW51hzy\nbDuQvUo5P9arsbMYP9lzsKa73QKBgQDYYcB9B/c4JiOkKs8+BIlI/FXmqArk7s0X\ndbmYizO/DQJiJI++Q5UJwz8W6g5hsyXv9UU6Qp5RGX63bPLcL6p4L8BC4UsRAGG2\nw/CRAHHK7vlgQyXeeqENyo/THDtCCEf0aroiOIG/9SrnQG1S1sn8ToQElMDCr/cz\nvy/xe93MJwKBgQC7nnl9Z2Kb/iBs1OE4kUGGRu7+hRxZpYvG3VsZF/q4I2cKlEgM\npQNamN5BnbMBoi78FPiSu6hzm4allMrhBurzs9SxKmN56xgpIPLQwMsMkYl8W67o\ne1O6mWasF7vjUpXimhwkovXm/jtP2WqgGMpT3Rng+jR65aUSGgJk9E5RFQKBgD+4\n6droUaGzeaOLB+UXqOZZiWKX8j1hJfzWqoWF2QNWbXFBmyNI+8cYPKge3YVgILf9\n3xk9LSps+6hA6XR2hRlH1rLbbiPfnOcZ5OqO2vQMVFxI6goOywcotBpTog/cKHSO\nSapyQaOqK6xWiNtwbaNj6/T9aZbsAzy1/QR8meDZAoGAFGfq5uoYssH5eseQa4Qo\nqxlqIiQIgNV6y9J0pYMeeYvCf8wUnQ+aw1ISlq1B/6HihljhibVMRLE7Azmt9rpg\n0Z6U0uyz1M61XmhWsp8KUSiWqgLnbjNAe5zmKW0ukMeDULscNUMZ1Y87XGlOeHZ1\nm7mFU0zVi6G0LGOK88IaNTY=\n-----END PRIVATE KEY-----\n",
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
        users.document(user_id).update({"thresholds": firestore.ArrayUnion([thresholds])})

        return "Successfully created"
    return "Could not set threshold"

if __name__ == "__main__":
    app.run(debug=True)