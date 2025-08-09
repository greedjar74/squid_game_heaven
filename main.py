import streamlit as st

from cat_scoring import cat_scoring
from word_relay import word_relay
from lotto import lotto
from word_guess import word_guess
# from rsp import rsp

def main_page():
    st.title("🦑오징어 게임 천국")
    st.write("재미있는 게임을 즐겨보세요!")

    st.markdown("### 게임 목록")
    st.markdown("1. 🐱 고양이 그리기")
    st.markdown("2. 🧠 끝말잇기 챗봇")
    st.markdown("3. 🎰 로또 시뮬레이션")
    st.markdown("4. 🤔 스무고개")
    st.markdown("5. ✊ 가위바위보 -> library 충돌.. 로컬으로 실행 가능")

page_names_to_funcs = {'Main Page': main_page,
                        '🐱 고양이 그리기': cat_scoring,
                        '🧠 끝말잇기 챗봇': word_relay,
                        '🎰 로또 시뮬레이션': lotto,
                        '🤔 스무고개': word_guess,}
                        #'✊ 가위바위보': rsp # 위에 추가해주세요

selected_page = st.sidebar.selectbox("게임 선택", page_names_to_funcs.keys())

page_names_to_funcs[selected_page]()