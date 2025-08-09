import os
import random
import json
import streamlit as st
from openai import OpenAI

# ---------- 기본 설정 ----------
st.set_page_config(page_title="스무고개", page_icon="🧠", layout="centered")

# ---------- 데이터셋 (주제별 미리 정해진 값) ----------
DATASETS = {
    "동물": ["고양이", "개", "코끼리", "사자", "펭귄", "여우", "기린", "돌고래", "독수리", "매", "올빼미", "펭귄", "플라밍고", "타조", "공작새", "갈매기", "앵무새", "까마귀", "햄스터", "코끼리", "하마", "곰", "여우", "늑대", "상어", "참치", "연어", "가오리", "피라냐", "메기", "날치", "악어", "코브라", "이구아나", "카멜레온", "거북이", "도마뱀", "두꺼비", "도롱뇽", "해파리", "오징어", "게", "가재", "불가사리"],
    "인물": ["알베르트 아인슈타인", "이순신", "손흥민", "넬슨 만델라", "마리 퀴리", "정약용", "잔다르크", "나폴레옹", "일런 머스크", "팀쿡", "다빈치", "쇼팽", "바흐", "톨스토이", "셰익스피어", "뭉크", "고흐", "미켈란젤로", "파블로", "피카소", "뉴턴", "아인슈타인", "스티븐 호킹", "갈릴리오 갈릴레이", "프레디 머큐리", "마이클 잭슨", "비틀즈", "비욘세", "아델", "아이유", "메시", "호날두", "우사인 볼트", "타이거 우즈", "김연아", "류현진", "커쇼", "조던"],
    "국가": ["대한민국", "일본", "미국", "프랑스", "브라질", "이집트", "호주", "중국", "인도", "스페인", "베트남", "대만", "오스트레일리아", "칠레", "덴마크", "러시아", "폴란드", "헝가리", "이탈리아", "포르투갈", "노르웨이", "영국", "독일", "베네수엘라", "브라질", "아르헨티나", "콜롬비아", "페루", "쿠바", "이집트", "나이지리아", "케냐", "에티오피아", "알제리", "모로코", "탄자니아", "우간다", "에티오피아", "모나코"],
    "캐릭터": ["마리오", "피카츄", "아이언맨", "헬로키티", "스폰지밥", "도라에몽", "피카추", "스폰지밥", "엘사", "손오공", "나루토", "루피", "조로", "상디", "마리오", "아이언맨", "토르", "스파이더맨", "캡틴아메리카", "헐크", "배트맨", "슈퍼맨", "조커", "해리포터", "셜록홈즈", "피터팬", "곰돌이 푸", "짱구", "코난"],
    "브랜드": ["삼성", "애플", "나이키", "아디다스", "코카콜라", "스타벅스", "푸마", "테슬라", "구글", "디올", "버버리", "구찌", "루이비통", "샤넬", "LG", "델", "현대", "마이크로소프트", "아우디", "벤츠", "말보로", "미즈노", "리복", "휠라", "리바이스", "화웨이", "샤오미", "로지텍", "레노버", "포드", "페라리", "롤스로이스", "람보르기니", "볼보", "포르쉐", "코카콜라", "하겐다즈", "KFC", "도미노피자", "피자헛", "버거킹", "맥도날드", "펩시", "하인즈", "코스트코"],
    "운동": ["펜싱", "승마", "철인3종", "축구", "야구", "농구", "테니스", "배드민턴", "수영", "복싱", "스케이트보드", "스키", "탁구", "헬스", "러닝", "마라톤", "자전거", "요가", "필라테스", "등산", "줄넘기", "서핑", "스트레칭", "MMA"],
}

# ---------- 유틸 ----------
def normalize(text: str) -> str:
    return (text or "").strip().lower().replace(" ", "")

@st.cache_data(show_spinner=False)
def generate_hints(api_key: str, topic: str, answer: str) -> list[str]:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    system = (
        "너는 퀴즈 힌트 생성기야. 사용자가 맞힐 정답을 바로 드러내지 말고, "
        "점점 구체적으로 접근하는 한국어 힌트 20개를 만들어. "
        "정답 단어나 동의어를 직접적으로 쓰지 마. 각 힌트는 1문장, 5~20자 내외. "
        "JSON만 반환: {\"hints\":[\"...\",...]}"
    )
    user = (
        f"주제: {topic}\n정답: {answer}\n"
        "요청: 정답을 유추할 수 있는 힌트 20개를 난이도 낮은→높은 순서로 만들어."
    )

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.7,
        )
        content = resp.choices[0].message.content
        data = json.loads(content)
        hints = data.get("hints", [])
        while len(hints) < 20:
            hints.append("특징을 더 관찰해 보세요.")
        return hints[:20]
    except Exception:
        return [
            "일상에서 자주 접할 수 있어요.",
            "대중에게 널리 알려져 있어요.",
            "관련 상품/콘텐츠가 많아요.",
            "특정 상징/이미지가 떠올라요.",
            "아주 유명한 이름이에요.",
        ]

# ---------- 세션 상태 초기화 ----------
def init_state():
    st.session_state.setdefault("topic", None)
    st.session_state.setdefault("answer", None)
    st.session_state.setdefault("hints", [])
    st.session_state.setdefault("hints_revealed", 0)
    st.session_state.setdefault("game_over", False)
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("api_key", "")

def word_guess():
    init_state()

    # ---------- 사이드바 ----------
    st.sidebar.title("🎮 스무고개")
    st.session_state["api_key"] = st.sidebar.text_input("OpenAI API Key", type="password", value=st.session_state["api_key"])
    restart = st.sidebar.button("게임 다시 시작", use_container_width=True)
    if restart:
        st.session_state.clear()
        st.cache_data.clear()
        st.rerun()

    with st.sidebar:
        st.markdown("#### 주제 선택")
        topic = st.selectbox("주제를 고르세요", options=["(선택)"] + list(DATASETS.keys()), index=0)
        start = st.button("게임 시작", disabled=(topic == "(선택)" or not st.session_state["api_key"]), use_container_width=True)

    # ---------- 게임 시작 로직 ----------
    if start:
        st.session_state["topic"] = topic
        st.session_state["answer"] = random.choice(DATASETS[topic])
        st.session_state["hints"] = generate_hints(st.session_state["api_key"], topic, st.session_state["answer"])
        st.session_state["hints_revealed"] = 0
        st.session_state["game_over"] = False
        st.session_state["messages"] = [
            {
                "role": "assistant",
                "content": f"주제는 **{topic}** 입니다. 정답을 맞혀 보세요! 필요하면 '힌트 보기' 버튼을 누르세요.",
            }
        ]
        st.rerun()

    # ---------- 본문 UI ----------
    st.title("🧠 스무고개 - GPT 힌트 퀴즈")

    if not st.session_state["topic"]:
        st.info("좌측 사이드바에서 주제를 선택하고 API 키를 입력한 뒤 **게임 시작**을 눌러주세요.")
        st.stop()

    for m in st.session_state["messages"]:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    col1, col2 = st.columns([3, 1])
    with col1:
        user_guess = st.chat_input("정답을 입력하세요…")
    with col2:
        hint_clicked = st.button(
            "힌트 보기",
            disabled=(st.session_state["game_over"] or st.session_state["hints_revealed"] >= 20),
        )

    if hint_clicked and not st.session_state["game_over"]:
        idx = st.session_state["hints_revealed"]
        if idx < 20:
            hint_text = st.session_state["hints"][idx]
            st.session_state["hints_revealed"] += 1
            st.session_state["messages"].append({"role": "assistant", "content": f"🔎 힌트 {idx+1}/20: {hint_text}"})
            st.rerun()

    if user_guess and not st.session_state["game_over"]:
        st.session_state["messages"].append({"role": "user", "content": user_guess})
        if normalize(user_guess) == normalize(st.session_state["answer"]):
            st.session_state["messages"].append({"role": "assistant", "content": "🎉 **정답입니다!** 게임이 종료되었어요."})
            st.session_state["game_over"] = True
        else:
            st.session_state["messages"].append({"role": "assistant", "content": "❌ 틀렸습니다."})
        st.rerun()

    with st.expander("게임 상태 보기", expanded=False):
        st.write({
            "주제": st.session_state["topic"],
            "힌트 제공": f"{st.session_state['hints_revealed']}/20",
            "게임 종료": st.session_state["game_over"],
        })

    if st.session_state["game_over"]:
        st.success(f"정답: {st.session_state['answer']}")
        st.info("좌측의 **게임 다시 시작** 버튼을 눌러 새 게임을 시작하세요.")
    else:
        remain = 20 - st.session_state["hints_revealed"]
        st.caption(f"남은 힌트: {remain}개")
