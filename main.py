import cv2
import os
import pickle
import face_recognition
import cvzone
import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

# Initialize the Firebase app
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://facetest-f8bfd-default-rtdb.firebaseio.com/",
    'storageBucket': "mawjudfirebase.appspot.com"
})


# Reference to the database
ref = db.reference()
bucket = storage.bucket()

# Open the camera
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# Load the encoding file
print("Loading Encode File ...")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
studentNames = {}

# Load student names from Firebase
for id in studentIds:
    student = ref.child(id).get()
    studentNames[id] = student['name']

print("Encode File Loaded")

while True:
    success, img = cap.read()
    # Resize the image for faster processing
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    # Find the faces in the current frame
    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)


    # Compare the current frame's encodings with the known encodings
    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                # Mark the student as present
                id = studentIds[matchIndex]
                ref.child(id).update({"present": True})

                # To locate the face
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                img = cvzone.cornerRect(img, bbox, rt=0)

                # Add the name of the detected person
                name = studentNames[id]
                font = cv2.FONT_HERSHEY_SIMPLEX
                scale = 1
                thickness = 2
                text_size = cv2.getTextSize(name, font, scale, thickness)[0]
                x1, y1 = int(bbox[0]), int(bbox[1] - text_size[1])
                cv2.rectangle(img, (x1, y1-22), (x1+text_size[0], y1+bbox[3]+text_size[1]), (255,255,255), cv2.FILLED)
                cv2.putText(img, name, (x1, y1), font, scale, (0,0,0), thickness)

                # Add the name of the detected person
                name = studentNames[id]
                ref.child(id).update({"name": name})

