import pyrebase

config = {
"apiKey": "AIzaSyDJ8_IAWiRwQQ7c2fYqV7TBiu92AdH0yq0",
"authDomain": "airquality-d611e.firebaseapp.com",
"projectId": "airquality-d611e",
"storageBucket": "airquality-d611e.appspot.com",
"messagingSenderId": "636721957126",
"appId": "1:636721957126:web:02ad2cf7c222b4b5013687",
"measurementId": "G-29Z39BMNP4",
"databaseURL": ""
}

firebase = pyrebase.initialize_app(config)

auth = firebase.auth()
email = "test@gmail.com"
password = "123456"

user = auth.create_user_with_email_and_password(email, password)

user = auth.sign_in_with_email_and_password(email, password)

auth.send_email_verification(user['idToken'])

