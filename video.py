import cv2
import tensorflow
import keras
from PIL import Image, ImageOps
import numpy as np
import playsound
import time

# 자세교정 알림 멘트
def sound_notice():
    return playsound.playsound('notice.mp3')

def preprocessing(frame):
    #사이즈 조정
    size = (224,224)
    frame_resized = cv2.resize(frame, size, interpolation=cv2.INTER_AREA)

    #이미지 정규화
    frame_normalized = (frame_resized.astype(np.float32) / 127.0)-1

    #이미지 차원 재조정 - 예측을 위해 reshape 해줌
    frame_reshaped = frame_normalized.reshape((1, 224, 224, 3))

    return frame_reshaped

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

# Load the model
#학습된 모델링 로딩
model = tensorflow.keras.models.load_model('keras_model.h5')

#카메라 객체(내장카메라)
capture = cv2.VideoCapture(0)

#카메라 프레임 사이즈 조절
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

#오자세감지 시간초 세팅
wrong_pose = 0

while True:
    ret, frame = capture.read()
    if ret == True:
        print("read success!")

    #이미지 뒤집기    ?????
    frame_fliped = cv2.flip(frame, 1)

    #이미지 출력     ??????
    cv2.imshow("VideoFrame", frame_fliped)

    # 1초마다 검사하며, videframe 창으로 아무 키나 누르게 되면 종료됨, 1ms동안 사용자가 키를 누르기를 기다림
    if cv2.waitKey(1) > 0:
        break


    #데이터 전처리
    preprocessed = preprocessing(frame_fliped)
    #예측
    prediction = model.predict(preprocessed)

    if prediction[0,0] < prediction[0,2] or prediction[0,1] < prediction[0,3]:
        print("오자세 판정!!")
        wrong_pose += 1

        #오자세가 10초 이상 지속되면 경고음 발생
        if wrong_pose % 10 == 0:
            wrong_pose = 0
            # 오자세 유지시 알림음
            print("거북이 됩니다 그러다")
            sound_notice()
            #계속 반복되게 안하려면 아래 주석 해제
            break
    else:
        print("자세가 바른 상태")
        wrong_pose = 0
# time.sleep(1)

#카메라 객체 반환
capture.release()
#화면에 나타난 윈도우들을 종료
cv2.destroyAllWindows()

