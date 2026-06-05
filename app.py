import streamlit as style
from google import genai
from google.genai import types
from google.genai.errors import APIError

# 페이지 설정
st.set_page_config(page_title="달콤살벌 연애상담소", page_icon="💖", layout="centered")
st.title("💖 달콤살벌 연애상담소")
st.caption("연애 고민, 썸, 이별 이야기까지 무엇이든 이야기해보세요. (gemini-2.5-flash-lite 적용)")

# 1. Streamlit Secrets에서 API 키 불러오기 및 클라이언트 초기화
try:
    # Streamlit Cloud 배포 환경 또는 로컬 .streamlit/secrets.toml 환경
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except KeyError:
    st.error("API 키를 찾을 수 없습니다. Streamlit Secrets에 'GEMINI_API_KEY'를 설정해주세요.")
    st.stop()
except Exception as e:
    st.error(f"초기화 중 오류가 발생했습니다: {e}")
    st.stop()

# 2. 세션 상태(Session State)로 채팅 기록 유지
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "안녕하세요! 당신의 연애 고민을 들어드릴 전문 상담사입니다. 어떤 고민이 있으신가요?"}
    ]

# 기존 채팅 메시지 화면에 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 3. 사용자 입력 처리
if user_input := st.chat_input("고민을 입력해보세요... (예: 썸남이 선톡을 안 해요)"):
    # 사용자 메시지 표시 및 저장
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # AI 답변 생성 과정 및 오류 처리
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # 페르소나 부여를 위한 시스템 명령어 설정
            system_instruction = (
                "당신은 공감 능력이 뛰어나면서도 때로는 뼈 때리는 조언을 해주는 전문 연애 상담사입니다. "
                "사용자의 고민에 진심으로 공감해주고, 심리학적 관점이나 현실적인 조언을 섞어서 "
                "친근한 말투(하오체나 존댓말을 섞은 다정한 톤)로 답변해주세요."
            )
            
            # API 호출 (gemini-2.5-flash-lite 사용)
            # 대화 기록 유지를 위해 전체 메시지 내역을 모델에 전달합니다.
            contents = [
                types.Content(
                    role="user" if m["role"] == "user" else "model",
                    parts=[types.Part.from_text(text=m["content"])]
                ) for m in st.session_state.messages
            ]

            response = client.models.generate_content(
                model='gemini-2.5-flash-lite',
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7, # 적당한 창의성과 감정 표현을 위한 설정
                )
            )
            
            ai_response = response.text
            message_placeholder.write(ai_response)
            
            # AI 메시지 세션에 저장
            st.session_state.messages.append({"role": "assistant", "content": ai_response})

        except APIError as ae:
            # 구글 API 관련 에러 처리 (할당량 초과, 잘못된 키 등)
            error_msg = f"구글 API 오류가 발생했습니다: {ae.message}"
            message_placeholder.error(error_msg)
        except Exception as e:
            # 기타 예상치 못한 에러 처리
            error_msg = f"죄송합니다, 답변을 생성하는 중 오류가 발생했습니다: {str(e)}"
            message_placeholder.error(error_msg)
