import streamlit as st
import random
import time

def lotto():
    st.title("🎰 로또 시뮬레이션")
    st.markdown("1부터 45 사이의 숫자 중 6개를 선택하세요.")

    # 사용자 숫자 선택
    user_numbers = st.multiselect("숫자 선택", options=list(range(1, 46)), max_selections=6)

    # 초기화
    if "drawn_numbers" not in st.session_state:
        st.session_state.drawn_numbers = []

    if "final_numbers" not in st.session_state:
        st.session_state.final_numbers = []

    # 색상 헬퍼 함수
    def get_color(n):
        if 1 <= n <= 10:
            return "orange"  # 노란색 대체
        elif 11 <= n <= 20:
            return "blue"
        elif 21 <= n <= 30:
            return "red"
        elif 31 <= n <= 40:
            return "black"
        elif 41 <= n <= 45:
            return "green"
        return "gray"

    # 번호 리스트를 HTML로 변환
    def format_numbers(nums):
        nums = sorted(nums)
        styled = [f"<span style='color: {get_color(n)}; font-weight: bold; font-size: 24px;'>{n}</span>" for n in nums]
        return " &nbsp; ".join(styled)

    # 리셋 버튼
    if st.button("🔄 리셋"):
        st.session_state.drawn_numbers = []
        st.session_state.final_numbers = []
        st.experimental_rerun()

    # 번호 추첨
    if len(user_numbers) == 6:
        user_numbers_sorted = sorted(user_numbers)
        st.markdown("🎯 당신의 번호:")
        st.markdown(format_numbers(user_numbers_sorted), unsafe_allow_html=True)

        if st.button("로또 번호 추첨 시작!"):
            st.session_state.drawn_numbers = []
            st.session_state.final_numbers = []

            placeholder = st.empty()

            # 번호 6개 추첨
            while len(st.session_state.drawn_numbers) < 6:
                available = list(set(range(1, 46)) - set(st.session_state.drawn_numbers))
                final_number = random.choice(available)

                # 숫자 변화 애니메이션 (1.5초 동안 0.1초 간격으로)
                for _ in range(15):  # 0.1초 × 15 = 1.5초
                    temp = random.choice(available)
                    placeholder.markdown(
                        f"<h1 style='text-align: center; color: {get_color(temp)};'>{temp}</h1>",
                        unsafe_allow_html=True,
                    )
                    time.sleep(0.1)

                # 최종 숫자 선택 및 저장
                st.session_state.drawn_numbers.append(final_number)
                st.session_state.final_numbers.append(final_number)
                placeholder.markdown(
                    f"<h1 style='text-align: center; color: {get_color(final_number)};'>{final_number} ✅</h1>",
                    unsafe_allow_html=True,
                )
                time.sleep(1)

            placeholder.empty()

            final_sorted = sorted(st.session_state.final_numbers)

            st.subheader("🎉 당첨 번호")
            st.markdown(format_numbers(final_sorted), unsafe_allow_html=True)

            # 결과 비교
            matched = len(set(user_numbers_sorted) & set(final_sorted))
            st.info(f"🎯 맞은 개수: {matched}개")
    else:
        st.warning("⚠️ 숫자를 6개 선택해주세요.")