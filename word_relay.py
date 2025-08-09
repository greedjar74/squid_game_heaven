import streamlit as st
from openai import OpenAI

def word_relay():
    # 🎯 Sidebar에서 사용자에게 API 키 입력 받기
    st.sidebar.title("🔐 OpenAI API 설정")
    api_key = st.sidebar.text_input("OpenAI API Key를 입력하세요", type="password")

    # 🧠 타이틀 및 설명
    st.title("🧠 끝말잇기 챗봇")

    # 🎯 승리 횟수 상태 초기화
    if "user_wins" not in st.session_state:
        st.session_state.user_wins = 0
    if "gpt_wins" not in st.session_state:
        st.session_state.gpt_wins = 0

    # 🧠 승리 횟수 표시
    st.markdown(f"🧑 사용자 승리: **{st.session_state.user_wins}** | 🤖 GPT 승리: **{st.session_state.gpt_wins}**")
    st.markdown("GPT와 대화 형식으로 끝말잇기를 즐겨보세요!")

    # 🔒 API 키 확인
    if not api_key:
        st.error("❌ OpenAI API Key가 입력되지 않았습니다. 사이드바에서 입력해주세요.")
        st.stop()

    # ✅ OpenAI Client
    client = OpenAI(api_key=api_key)

    # 🎮 상태 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "game_over" not in st.session_state:
        st.session_state.game_over = False

    # 📜 끝말잇기 프롬프트 생성
    def generate_prompt(user_word, history):
        prompt = f"""
    너는 끝말잇기 게임을 하는 챗봇이야.
    규칙은 다음과 같아:
    1. 사용자가 말한 단어의 마지막 글자로 시작하는 단어를 제시해야 해.
    2. 단어는 중복되면 안돼.
    3. 일반적인 명사여야 해 (고유명사, 외래어, 줄임말 금지).
    4. 말할 단어가 없거나 규칙을 어기면 "항복이야!"라고 말해.

    지금까지 나온 단어들: {', '.join(history)}
    사용자의 단어: {user_word}
    GPT의 다음 단어는?
    """
        return prompt

    # 📥 유저 입력창
    user_input = st.chat_input("당신의 단어를 입력하세요")

    # 💬 이전 메시지 렌더링
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 🔘 사이드바 버튼: 승리 및 리셋
    st.sidebar.markdown("### 🏆 수동 점수 조정 / 게임 초기화")
    col1, col2 = st.sidebar.columns(2)
    if col1.button("🧑 사용자 승리"):
        st.session_state.user_wins += 1
        st.session_state.messages = []
        st.session_state.game_over = False
        st.experimental_rerun()
    if col2.button("🤖 로봇 승리"):
        st.session_state.gpt_wins += 1
        st.session_state.messages = []
        st.session_state.game_over = False
        st.experimental_rerun()

    # 🔄 리셋 버튼 (점수는 그대로 유지)
    if st.sidebar.button("🔄 게임 다시 시작"):
        st.session_state.messages = []
        st.session_state.game_over = False
        st.experimental_rerun()

    # 🚀 게임 진행
    if user_input and not st.session_state.game_over:
        user_input = user_input.strip()

        # 중복 방지용 히스토리
        history_words = [m["content"] for m in st.session_state.messages if m["role"] in ["user", "assistant"]]

        if user_input in history_words:
            with st.chat_message("assistant"):
                st.error("⚠️ 이미 사용된 단어입니다. 다른 단어를 입력하세요.")
        else:
            # 유저 메시지 저장
            st.chat_message("user").markdown(user_input)
            st.session_state.messages.append({"role": "user", "content": user_input})

            try:
                # GPT 호출
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "너는 똑똑한 끝말잇기 챗봇이야."},
                        {"role": "user", "content": generate_prompt(user_input, history_words)}
                    ],
                    temperature=0.7,
                    max_tokens=50
                )

                gpt_reply = response.choices[0].message.content.strip()

                with st.chat_message("assistant"):
                    st.markdown(gpt_reply)

                st.session_state.messages.append({"role": "assistant", "content": gpt_reply})

                # 종료 조건
                if "항복" in gpt_reply or "모르겠" in gpt_reply:
                    st.session_state.game_over = True
                    st.session_state.user_wins += 1
                    st.warning("🎉 당신이 이겼습니다! GPT가 항복했어요.")
                elif gpt_reply in history_words:
                    st.session_state.game_over = True
                    st.session_state.user_wins += 1
                    st.warning("🎉 GPT가 중복된 단어를 사용했습니다. 당신의 승리!")

            except Exception as e:
                with st.chat_message("assistant"):
                    st.error(f"❌ GPT 호출 실패: {e}")
