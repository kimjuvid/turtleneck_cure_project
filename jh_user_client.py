import sys
import threading
import socket
import cv2
import tensorflow
import keras
import numpy as np
import playsound
import time
from PyQt5 import uic
from PyQt5.QtWidgets import *

#UI파일 연결
#단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
form_class = uic.loadUiType("user_client1.ui")[0]

#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 소켓생성
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 서버 주소 입력
        self.ip ='localhost'
        self.port = 9999
        self.sock.connect((self.ip, self.port))
        # 확인용
        print("서버와 연결완료")

        #ui 사이즈 고정
        self.setFixedSize(1071, 650)

        #기본 화면전화 코드
        self.pushButton_2.clicked.connect(lambda : self.stackedWidget.setCurrentIndex(1))   #회원가입 창 이동
        self.pushButton_5.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))    #회원가입 창에서 홈으로
        self.pushButton_8.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))    #메인창에서 홈으로
        self.pushButton_10.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))   #오늘의 운동창에서 메인으로
        self.pushButton_12.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(3))  #오늘의 운동으로 이동
        self.pushButton.clicked.connect(self.login)             #로그인시도
        self.pushButton_3.clicked.connect(self.id_checking)     #아이디 중복검사시도
        self.pushButton_4.clicked.connect(self.member_join)     #회원가입 시도시
        self.pushButton_9.clicked.connect(self.exercise)       #오늘의 운동
        self.pushButton_11.clicked.connect(self.pose_reform)  # 실시간 자세교정으로 이동
        # self.stackedWidget.setCurrentIndex(3)

# 로그인
    def login(self):
        print('로그인 버튼 클릭 가능')
        if not self.id.text() or not self.pw.text():
            QMessageBox.warning(self, '입력 누락', '모든 정보를 입력해야 합니다')
        else:
            #서버에 아이디 로그인 일치 여부 확인
            self.sock.send(f'login_check/{self.id.text()}/{self.pw.text()}'.encode())   #######로그인시 구분자 / (login_check, 아이디, 비번)
            print('전송 완료')
            #일치 시
            while True:
                rec = self.sock.recv(1024).decode()
                if rec == 'login_check_ok':
                    # 로그인 성공시
                    QMessageBox.about(self, '로그인 완료', '로그인이 완료되었습니다.')
                    self.id.clear()
                    self.pw.clear()
                    self.stackedWidget.setCurrentIndex(2)
                    break
                else:
                    # 로그인 실패시
                    QMessageBox.warning(self, '로그인 실패', 'ID와 PW를 다시 확인해 주세요')
                    self.id.clear()
                    self.pw.clear()
                    break

# 회원가입
    def member_join(self):
        if not self.member_name.text() or not self.member_id.text() or not self.member_pw.text() or not self.member_number.text():
            QMessageBox.warning(self, '입력 누락', '회원 가입 정보를 모두 기재하셔야합니다.')
            self.member_name.clear()
            self.member_id.clear()
            self.member_pw.clear()
            self.member_number.clear()
        else:
            self.sock.send(f'member_join/{self.member_name.text()}/{self.member_gender.currentText()}/{self.member_id.text()}/{self.member_pw.text()}/{self.member_number.text()}'.encode())
            while True:
                rec = self.sock.recv(1024).decode()
                if rec == 'member_join_ok':
                    QMessageBox.about(self, '회원가입 완료', '회원가입이 완료되었습니다.')
                    self.member_name.clear()
                    self.member_id.clear()
                    self.member_pw.clear()
                    self.member_number.clear()
                    self.stackedWidget.setCurrentIndex(0)
                    break
                else:
                    QMessageBox.warning(self, '회원가입 실패', '중복되는 ID를 사용하였습니다.')
                    self.member_name.clear()
                    self.member_id.clear()
                    self.member_pw.clear()
                    self.member_number.clear()
                    break

# 아이디 중복검사
    def id_checking(self):
        if not self.member_id.text():
            QMessageBox.warning(self, '입력 누락', 'ID를 입력해주세요.')
        else:
            self.sock.send(f'id_check/{self.member_id.text()}'.encode())
            while True:
                rec = self.sock.recv(1024).decode()
                if rec == 'id_ok':
                    QMessageBox.about(self, '사용 가능 ID', '사용이 가능한 ID입니다')
                    break
                else:
                    QMessageBox.warning(self, '사용 불가 ID', '이미 존재하는 ID입니다.')
                    self.member_id.clear()
                    break

# 실시간 자세 교정
    def pose_reform(self):
        # 자세교정 알림 멘트
        def sound_notice():
            return playsound.playsound("notice.mp3")

        def preprocessing(frame):
            # 사이즈 조정
            size = (224, 224)
            frame_resized = cv2.resize(frame, size, interpolation=cv2.INTER_AREA)

            # 이미지 정규화
            frame_normalized = (frame_resized.astype(np.float32) / 127.0) - 1

            # 이미지 차원 재조정 - 예측을 위해 reshape 해줌
            frame_reshaped = frame_normalized.reshape((1, 224, 224, 3))

            return frame_reshaped

        # Disable scientific notation for clarity
        np.set_printoptions(suppress=True)

        # Load the model
        # 학습된 모델링 로딩
        model = tensorflow.keras.models.load_model('keras_model.h5')

        # 카메라 객체(내장카메라)
        capture = cv2.VideoCapture(0)

        # 카메라 프레임 사이즈 조절
        # capture.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        # capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

        # 오자세감지 시간초 세팅
        wrong_pose = 0

        while True:
            ret, frame = capture.read()
            if ret == True:
                print("read success!")

            # 이미지 뒤집기    ?????
            frame_fliped = cv2.flip(frame, 1)

            # 이미지 출력     ??????
            cv2.imshow("VideoFrame", frame_fliped)

            # 1초마다 검사하며, videframe 창으로 아무 키나 누르게 되면 종료됨, 1ms동안 사용자가 키를 누르기를 기다림
            if cv2.waitKey(1) > 0:
                break

            # 데이터 전처리
            preprocessed = preprocessing(frame_fliped)
            # 예측
            prediction = model.predict(preprocessed)

            if prediction[0, 0] < prediction[0, 2] or prediction[0, 1] < prediction[0, 3]:
                print("오자세 판정!!")
                wrong_pose += 1

                # 오자세가 10초 이상 지속되면 경고음 발생
                try:
                    if wrong_pose % 15 == 0:
                        wrong_pose = 1
                        # 오자세 유지시 알림음
                        print("거북이 됩니다 그러다")
                        sound_notice()
                        self.sock.send('1'.encode())
                        # 계속 반복되게 안하려면 아래 주석 해제
                        # break
                except:
                    pass
            else:
                print("자세가 바른 상태")
                wrong_pose = 1
            # 타임슬립 사용시 영상 재생이 원활하지 않은 문제점이 있음
            # time.sleep(1)

        # 카메라 객체 반환
        capture.release()
        # 화면에 나타난 윈도우들을 종료
        cv2.destroyAllWindows()

# 오늘의 운동
    def exercise(self):
        self.sock.send('get_excer'.encode())
        while True:
            rec = self.sock.recv(8192).decode()
            self.textBrowser.append(f'{rec}')
            break


if __name__ == "__main__":
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)
    #WindowClass의 인스턴스 생성
    myWindow = WindowClass()
    #프로그램 화면을 보여주는 코드
    myWindow.show()
    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()