import streamlit as st
from pages import tts_page, stt_page, tts2_page,stt2_page
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# 페이지 구성 설정 (메인 파일에서만 설정)
st.set_page_config(
    page_title="Cho pro AI 서비스",
    page_icon="🎤",
    layout="wide"
)


def main():
    # 사이드바에 제목 설정
    st.sidebar.title("🌟 Cho pro AI 서비스")  # 사이드바 상단의 제목과 아이콘
    st.sidebar.markdown("음성 변환 서비스를 제공합니다.")

    # 메인 화면 타이틀
    st.markdown("<div class='title'>AI 음성 변환 서비스</div>", unsafe_allow_html=True)
    st.markdown("<div class='description'>텍스트와 음성을 서로 변환하여 편리하게 활용할 수 있습니다.</div>", unsafe_allow_html=True)
    st.write("")  # 여백 추가

    # 서비스 선택
    page = st.sidebar.selectbox(
    "🔍 서비스 선택", 
    ["메인", "TTS무료 (텍스트 → 음성)","TTS유료 (텍스트 → 음성)","STT무료 (음성 → 텍스트)","STT유료 (음성 → 텍스트)"]
)

    
    # 선택한 페이지에 따라 다른 화면 표시
    if page == "메인":
        st.markdown("### 제공하는 서비스")
        st.write("- **TTS**: 텍스트를 음성으로 변환하여 저장할 수 있습니다.")
        st.write("- **STT**: 음성을 텍스트로 변환하고 요약할 수 있습니다.")
    elif page == "TTS유료 (텍스트 → 음성)":
        tts_page.render_page()
    elif page == "TTS무료 (텍스트 → 음성)":
        tts2_page.render_page()
    elif page == "STT유료 (음성 → 텍스트)":
        stt2_page.render_page()
    elif page == "STT무료 (음성 → 텍스트)":
        stt_page.render_page()

if __name__ == "__main__":
    main()
