import face_recognition
import cv2
import numpy as np
import sqlite3
from datetime import datetime
import serial
from playsound import playsound
from flask import Flask, render_template, Response


process_this_frame = True
#온도 저장 변수
temp = 0
#이름 저장 변수
f_name = ""
#얼굴인식 온도측정단계를 구분하기 위한 상태변수
state = 1
app = Flask(__name__)
#중첩된 이름 변수, 중첩 횟수
OL_name = ""
cnt = 0
cap = cv2.VideoCapture(0)

#serial통신 출력/온도 센서 함수
def Ardread():
    global temp
    ARD = serial.Serial("COM8", 9600)
    def Decode(valuable):
        valuable = valuable.decode()
        valuable = str(valuable)
        return valuable

    if ARD.readable():
        LINE = ARD.readline()
        return Decode(LINE)

# 데이터베이스 입력 함수
def write_database(x, y):
    conn = sqlite3.connect("project.db")
    cursor = conn.cursor()

    nm = x
    temp = y
    n_route = '->podium'

    if nm != '' and temp != 0:
        select_name = "SELECT name FROM PI WHERE name = ?"
        # select_number = "SELECT number FROM PI WHERE name = ?"
        select_route = "SELECT route FROM PI WHERE name = ?"

        # 이름 데이터 추출
        cursor.execute(select_name, (nm,))
        PI_name = cursor.fetchone()
        str(PI_name)
        conn.commit()

        # 전화번호 데이터 추출
        # cursor.execute(select_number, (nm,))
        # PI_number = cursor.fetchone()

        # 이동경로 데이터 추출
        cursor.execute(select_route, (nm,))
        PI_route = cursor.fetchone()
        conn.commit()
        str_route = str(PI_route)
        str_num = len(str_route) - 3
        final_name = str_route[2:str_num]
        route = final_name + n_route

        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")

        insert_er = "INSERT INTO ER(name,temp,route,time) VALUES(?,?,?,?)"
        cursor.execute(insert_er, (nm, temp, route, current_time))
        conn.commit()

        nm = ""
        temp = 0

    conn.close()  # data

# 얼굴인식 함수
def generate():
    global cnt
    global face_names
    global face_encodings
    global face_locations
    global process_this_frame
    global f_name
    global OL_name
    global state
    global temp
    global app

    byeongcheol_image = face_recognition.load_image_file("byeong_cheol.jpg")
    byeongcheol_face_encoding = face_recognition.face_encodings(byeongcheol_image)[0]

    giyeong_image = face_recognition.load_image_file("gi_yeong.jpg")
    giyeong_face_encoding = face_recognition.face_encodings(giyeong_image)[0]

    huidon_image = face_recognition.load_image_file("hui_don.jpg")
    huidon_face_encoding = face_recognition.face_encodings(huidon_image)[0]

    kyungseok_image = face_recognition.load_image_file("kyung_seok.jpg")
    kyungseok_face_encoding = face_recognition.face_encodings(kyungseok_image)[0]

    junsoo_image = face_recognition.load_image_file("jun_soo.jpg")
    junsoo_face_encoding = face_recognition.face_encodings(junsoo_image)[0]

    yeonjae_image = face_recognition.load_image_file("yeon_jae.jpeg")
    yeonjae_face_encoding = face_recognition.face_encodings(yeonjae_image)[0]

    sangwoo_image = face_recognition.load_image_file("sang_woo.JPG")
    sangwoo_face_encoding = face_recognition.face_encodings(sangwoo_image)[0]

    messi_image = face_recognition.load_image_file("messi.jpeg")
    messi_face_encoding = face_recognition.face_encodings(messi_image)[0]

    dongju_image = face_recognition.load_image_file("dong_ju.jpeg")
    dongju_face_encoding = face_recognition.face_encodings(dongju_image)[0]

    deokmin_image = face_recognition.load_image_file("deok_min.jpeg")
    deokmin_face_encoding = face_recognition.face_encodings(deokmin_image)[0]

    dohwan_image = face_recognition.load_image_file("do_hwan.jpeg")
    dohwan_face_encoding = face_recognition.face_encodings(dohwan_image)[0]

    # Create arrays of known face encodings and their names
    known_face_encodings = [
        yeonjae_face_encoding,
        sangwoo_face_encoding,
        messi_face_encoding,
        dongju_face_encoding,
        deokmin_face_encoding,
        dohwan_face_encoding,
        kyungseok_face_encoding,
        junsoo_face_encoding,
        byeongcheol_face_encoding,
        giyeong_face_encoding,
        huidon_face_encoding

    ]
    known_face_names = [
        "jeon yeong jae",
        "park sang woo",
        "lionel messi",
        "park dong ju",
        "kim deok min",
        "go do hwan",
        "oh kyung seok",
        "kim jun soo",
        "moon byeong cheol",
        "lee gi yeong",
        "yang hui don"
    ]
    while True:

        if (state == 1):
            ## read the camera frame
            success, frame = cap.read()
            if not success:
                break
            else:
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

                rgb_small_frame = small_frame[:, :, ::-1]

                if process_this_frame:
                    # Find all the faces and face encodings in the current frame of video
                    face_locations = face_recognition.face_locations(rgb_small_frame)
                    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                    face_names = []
                    for face_encoding in face_encodings:
                        # See if the face is a match for the known face(s)
                        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                        name = "Unknown"
                        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                        best_match_index = np.argmin(face_distances)
                        if matches[best_match_index]:
                            name = known_face_names[best_match_index]

                            if OL_name == name:
                                cnt += 1
                            else:
                                OL_name = name

                        face_names.append(name)

                process_this_frame = not process_this_frame

                # Display the results
                for (top, right, bottom, left), name in zip(face_locations, face_names):
                    # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4

                    # 얼굴인식 박스 만들기
                    cv2.rectangle(frame, (left, top), (right, bottom), (255, 255, 255), 2)

                    # 이름 쓰기
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (255, 255, 255), cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (0, 0, 0), 1)

                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

            if cnt == 5:
                f_name = OL_name
                OL_name = ""
                playsound("success_in_face_recognition.wav")
                playsound("temp_start.mp3")
                cnt = 0

                temp = float(Ardread())
                playsound("success.wav")


                if temp <= 37.5:
                    playsound("normaltemp.mp3") #정상온도 측정 안내 음성
                    write_database(f_name, temp)

                elif temp > 37.5:
                    playsound("alarm.mp3") #접근제한 안내 음성



                f_name = ""
                temp = 0


    cap.release()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/list')
def ppl():
    con = sqlite3.connect('project.db')
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("SELECT * FROM ER")
    rows = cur.fetchall()
    print(rows)
    return render_template('ppl.html', rows=rows)

if __name__ == "__main__":
    app.run(debug=True, threaded= True)


