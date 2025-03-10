#!/usr/bin/env python

import sys, os, cv2
import numpy as np

import rospy

from geometry_msgs.msg import Twist
from std_msgs.msg import String

pub = rospy.Publisher('cmd_vel', Twist, queue_size=1)

speed = 0.3
turn = 1.0

face_path = "/home/bcsh/robot_ws/src/match_mini/scripts/data"
face_name = "thief"


def read_images(path, sz=None):
    c = 0
    X, y = [], []
    names = []
    for dirname, dirnames, filenames in os.walk(path):
        for subdirname in dirnames:
            subject_path = os.path.join(dirname, subdirname)
            for filename in os.listdir(subject_path):
                try:
                    if (filename == ".directory"):
                        continue
                    filepath = os.path.join(subject_path, filename)
                    im = cv2.imread(os.path.join(subject_path, filename), cv2.IMREAD_GRAYSCALE)
                    if (im is None):
                        print("image" + filepath + "is None")
                    if (sz is not None):
                        im = cv2.resize(im, sz)
                    X.append(np.asarray(im, dtype=np.uint8))
                    y.append(c)
                except:
                    print("unexpected error")
                    raise
            c = c + 1
            names.append(subdirname)
    return [names, X, y]


def face_rec():
    [names, X, y] = read_images(face_path)
    y = np.asarray(y, dtype=np.int32)
    # model = cv2.face_EigenFaceRecognizer.create()
    model = cv2.face.LBPHFaceRecognizer_create()
    model.train(np.asarray(X), np.asarray(y))

    face_cascade = cv2.CascadeClassifier(
        '/home/bcsh/robot_ws/src/match_mini/scripts/cascades/haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0)
    cv2.namedWindow("face_detector", 0)
    print(cap)
    cv2.resizeWindow("face_detector", 480, 320)
    while True:
        ret, frame = cap.read()
        x, y = frame.shape[0:2]
        small_frame = cv2.resize(frame, (int(y / 2), int(x / 2)))
        result = small_frame.copy()
        gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            result = cv2.rectangle(result, (x, y), (x + w, y + h), (255, 0, 0), 2)
            roi = gray[y:y + h, x:x + w]
            try:
                roi = cv2.resize(roi, (200, 200), interpolation=cv2.INTER_LINEAR)
                [p_label, p_confidence] = model.predict(roi)
                cv2.putText(result, names[p_label], (x, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2)

                print("p_confidence = " + str(p_confidence) + "  name=" + names[p_label])
                if p_confidence > 30 and names[p_label] == face_name:
                    offset_x = ((x + w) / 2 - 240)
                    target_area = w * h
                    print("distance")
                    print(target_area)
                    linear_vel = 0
                    angular_vel = 0

                    if target_area < 5000:
                        linear_vel = 0.35
                    elif target_area < 8000:
                        linear_vel = 0.30  # change
                    elif target_area < 35000:
                        linear_vel = 0.20
                    elif target_area < 950000:
                        linear_vel = 0.15
                    else:
                        linear_vel = 0.0

                    if offset_x > 0:
                        angular_vel = -0.2

                    if offset_x < 0:
                        angular_vel = 0.2
                    update_cmd(linear_vel, angular_vel)


            except:
                continue
        cv2.imshow("face_detector", result)
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()


def update_cmd(linear_speed, angular_speed):
    twist = Twist()
    twist.linear.x = 1 * linear_speed;
    twist.linear.y = 1 * linear_speed;
    twist.linear.z = 1 * linear_speed;
    twist.angular.x = 0;
    twist.angular.y = 0;
    twist.angular.z = 1 * angular_speed
    pub.publish(twist)


def callback(msg):
    global face_path
    global face_name
    if msg.data == "goodperson":
        face_name = "goodperson"
    if msg.data == "thief":
        face_name = "thief"
    face_rec()


if __name__ == "__main__":
    rospy.init_node('face_detector')
    rospy.Subscriber("auto_face", String, callback)

    rospy.spin()


