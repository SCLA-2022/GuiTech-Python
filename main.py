import cv2
import mediapipe as mp
import time
from flask import Flask, render_template, Response
app = Flask(__name__)

camera = cv2.VideoCapture(0)

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

pTime = 0
cTime = 0


def hand_tracking(camera_frame):
    image_rgb = cv2.cvtColor(camera_frame, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)
    # print(results.multi_hand_landmarks)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark):
                # print(id,lm)
                h, w, c = camera_frame.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                print(id, cx, cy)
                if id == 0:
                    cv2.circle(camera_frame, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

            mpDraw.draw_landmarks(camera_frame, handLms, mpHands.HAND_CONNECTIONS)

            # cv2.imshow("Image", camera_frame)
            # cv2.waitKey(1)


def gen_frames():
    while True:
        success, frame = camera.read()
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if not success:
            break
        else:
            hand_tracking(frame)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/camera_feed')
def camera_feed():
    return render_template('camera_feed.html')


@app.route('/video_camera')
def video_camera():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run()
