'''
import streamlit as st
import cv2
import mediapipe as mp
from mediapipe.framework.formats import landmark_pb2
import numpy as np
import random
import time

def rsp():
    # 점수 상태 초기화
    if 'user_score' not in st.session_state:
        st.session_state.user_score = 0
    if 'robot_score' not in st.session_state:
        st.session_state.robot_score = 0
    if 'run' not in st.session_state:
        st.session_state.run = False

    # 상단 점수 표시
    score_placeholder = st.empty()
    score_placeholder.markdown(f"### 사용자 🧑: {st.session_state.user_score} &nbsp;&nbsp;&nbsp;&nbsp; 로봇 🤖: {st.session_state.robot_score}")

    st.title("안 내면 진다 가위바위보!")

    start_stop = st.button("▶️ 시작 / 정지", key="startstop")
    if start_stop:
        st.session_state.run = not st.session_state.run

    # Mediapipe 손 인식 초기화
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=float(0.7),
        min_tracking_confidence=float(0.5)
    )
    drawing_spec = mp_drawing.DrawingSpec(thickness=5, circle_radius=4, color=(255, 0, 0))


    # 이모지 매핑
    emoji = {"가위": "✌️", "바위": "✊", "보": "🖐️", "모름": "❓"}

    # 함수: 손 모양 인식
    def detect_gesture(landmarks):
        fingers = []
        tip_ids = [4, 8, 12, 16, 20]

        # 엄지
        fingers.append(int(landmarks.landmark[tip_ids[0]].x < landmarks.landmark[tip_ids[0] - 1].x))

        # 나머지 손가락
        for i in range(1, 5):
            fingers.append(int(landmarks.landmark[tip_ids[i]].y < landmarks.landmark[tip_ids[i] - 2].y))

        if fingers == [0, 1, 1, 0, 0]:
            return "가위"
        elif fingers == [0, 0, 0, 0, 0]:
            return "바위"
        elif fingers == [0, 1, 1, 1, 1] or fingers == [1, 1, 1, 1, 1]:
            return "보"
        else:
            return "모름"

    # 함수: 승패 판정
    def judge(user, robot):
        if user == robot:
            return "비김"
        elif (user == "가위" and robot == "보") or \
            (user == "바위" and robot == "가위") or \
            (user == "보" and robot == "바위"):
            return "승리"
        else:
            return "패배"

    # 화면 영역
    frame_placeholder = st.empty()
    vs_placeholder = st.empty()
    result_placeholder = st.empty()

    # 웹캠 연결
    cap = cv2.VideoCapture(0)

    while st.session_state.run:
        start_time = time.time()
        detected = "모름"

        # 🎮 3초 동안 손 인식
        while time.time() - start_time < 3:
            ret, frame = cap.read()
            if not ret:
                continue

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            if results.multi_hand_landmarks:
                for lm in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        frame,
                        lm,
                        mp_hands.HAND_CONNECTIONS,
                        landmark_drawing_spec=drawing_spec,      # 점
                        connection_drawing_spec=drawing_spec     # 선
                    )
                    detected = detect_gesture(lm)

            frame_placeholder.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB")
            time.sleep(0.05)

        # 👾 로봇 선택
        robot_choice = random.choice(["가위", "바위", "보"])
        outcome = judge(detected, robot_choice)

        # 🧠 결과 표시
        vs_text = f"<div style='font-size:50px;'>🤖: {emoji[robot_choice]}</div>"
        vs_placeholder.markdown(vs_text, unsafe_allow_html=True)

        if outcome == "승리":
            st.session_state.user_score += 1
            result_placeholder.markdown("<div style='font-size:50px; color:green;'>🎉 당신의 승리! 🎉</div>", unsafe_allow_html=True)
            st.balloons()
        elif outcome == "패배":
            st.session_state.robot_score += 1
            result_placeholder.markdown("<div style='font-size:50px; color:red;'>😢 패배했습니다 😢</div>", unsafe_allow_html=True)
        else:
            result_placeholder.markdown("<div style='font-size:50px;'>🤝 비겼습니다 🤝</div>", unsafe_allow_html=True)

        # 상단 점수 갱신
        score_placeholder.markdown(f"### 사용자 🧑: {st.session_state.user_score} &nbsp;&nbsp;&nbsp;&nbsp; 로봇 🤖: {st.session_state.robot_score}")

        # ⏳ 결과 5초간 유지 후 다음 라운드
        time.sleep(2)
        vs_placeholder.empty()
        result_placeholder.empty()

    # 종료 후 해제
    cap.release()
'''