import cv2
import pickle
import face_recognition
import cvzone
import numpy as np
import firebase_admin
import time
from firebase_admin import credentials
from firebase_admin import storage
from firebase_admin import firestore


# Initialize the Firebase app
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': "mawjudfirebase.appspot.com"
})

# Reference to the database
db = firestore.client()
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
# print(studentIds)
print("Encode File Loaded")

counter = 0
id = -1
imgStudent = []
total_days = 0
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
                # To locate the face
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 20 + y1, x2 - x1, y2 - y1
                img = cvzone.cornerRect(img, bbox, rt=0)

                # Mark the student as present
                id = studentIds[matchIndex]
                if counter == 0:
                    cvzone.putTextRect(img, "Loading", (220, 200))
                    cv2.imshow("Face Attendance", img)
                    cv2.waitKey(1)
                    counter = 1

        if counter != 0:

            if counter == 1:
               # Get the Data
               current_course_ref = db.collection('currentCourse').document('dJnBjGDTmBKfW7N4ltCB').get()
               if current_course_ref.exists:
                  course_id = current_course_ref.to_dict()['courseId']
               course_ref = db.collection('Courses').document(course_id).collection('Students').document(id)

               # Get the Image from the storage
               blob = bucket.get_blob(f'Student/{id}.jpg')
               array = np.frombuffer(blob.download_as_string(), np.uint8)
               imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

               # Update data of attendance
               course_ref.update({'attendance': 'present'})

               # Wait for 7 seconds
               time.sleep(7)

               # Delete the "present" word from attendance
               course_ref.update({'attendance': ''})
               course_ref.update({'total_days': firestore.Increment(1)})


    else:
        counter = 0

    cv2.imshow("Face Attendance", img)
    cv2.waitKey(1)
