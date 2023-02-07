import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Initialize the Firebase app
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://facetest-f8bfd-default-rtdb.firebaseio.com/"

})

# Connect to the Firebase database
ref = db.reference('Students')

data = {
    "439010":
        {
            "name": "lujain Hassan",
            "ID": 439010,

        },
    "439012":
        {
            "name": "lama mmm",
            "ID": 439012,

        },
    "439013":
        {
            "name": "fatimah has",
            "ID": 439013,

        }
}

for key, value in data.items():
    ref.child(key).set(value)