import streamlit as st
import os
import openai
from datetime import datetime
from dotenv import load_dotenv
import base64

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)

def detect_language(text):
    """입력된 텍스트의 언어를 감지"""
    # 간단한 언어 감지 로직
    korean = sum(1 for c in text if ord('가') <= ord(c) <= ord('힣'))
    english = sum(1 for c in text if ord('a') <= ord(c) <= ord('z') or ord('A') <= ord(c) <= ord('Z'))
    japanese = sum(1 for c in text if ord('ぁ') <= ord(c) <= ord('ヿ'))
    
    if korean > english and korean > japanese:
        return "한국어"
    elif japanese > english and japanese > korean:
        return "일본어"
    else:
        return "영어"

def get_voice_recommendations(text):
    """텍스트 분석을 통한 음성 추천"""
    language = detect_language(text)
    
    recommendations = {
        "한국어": ["nova"],  # 한국어에 적합한 음성
        "일본어": ["alloy"],    # 일본어에 적합한 음성
        "영어": ["all"]                 # 영어는 모든 음성 적합
    }
    
    return recommendations.get(language, ["all"])

def render_page():
    st.header("고급 TTS (텍스트 → 음성) 변환 서비스")
    
    # 기본 음성 설정
    voice_options = {
        "alloy": "Alloy - 균형 잡힌 중성적인 목소리",
        "echo": "Echo - 깊이 있는 남성 목소리",
        "fable": "Fable - 따뜻한 중성적인 목소리",
        "onyx": "Onyx - 강력한 남성 목소리",
        "nova": "Nova - 전문적인 여성 목소리",
        "shimmer": "Shimmer - 밝은 여성 목소리"
    }

    # 텍스트 입력
    col1, col2 = st.columns([2, 1])
    with col1:
        prompt = st.text_area(
            "변환할 텍스트를 입력하세요:",
            value="여기에 텍스트를 입력하세요",
            height=150
        )
    
    with col2:
        st.markdown("### 텍스트 분석")
        if prompt and prompt != "여기에 텍스트를 입력하세요":
            detected_lang = detect_language(prompt)
            st.write(f"감지된 언어: {detected_lang}")
            recommended_voices = get_voice_recommendations(prompt)
            if recommended_voices[0] != "all":
                st.write("추천 음성:")
                for voice in recommended_voices:
                    st.write(f"- {voice_options[voice]}")

    # 고급 설정 섹션
    with st.expander("고급 설정"):
        col3, col4 = st.columns(2)
        with col3:
            # 성우 선택 드롭다운
            voice_labels = list(voice_options.values())
            selected_label = st.selectbox("성우를 선택하세요:", voice_labels)
            selected_voice = [k for k, v in voice_options.items() if v == selected_label][0]
            
            # 샘플 오디오 재생
            st.subheader("샘플 음성")
            sample_audio_path = f"simple/{selected_voice}.mp3"
            try:
                with open(sample_audio_path, "rb") as audio_file:
                    audio_bytes = audio_file.read()
                    st.audio(audio_bytes, format="audio/mp3")
            except FileNotFoundError:
                st.warning("샘플 준비 중입니다.")
        
        with col4:
            # 파일 형식 및 품질 설정
            selected_format = st.selectbox(
                "파일 형식:",
                ["MP3", "WAV", "OGG", "M4A"],
                help="출력 파일의 형식을 선택하세요"
            ).lower()
            
            model = st.selectbox(
                "음성 품질:",
                ["tts-1", "tts-1-hd"],
                format_func=lambda x: "일반 품질" if x == "tts-1" else "고품질",
                help="고품질은 더 자연스럽지만 처리 시간이 깁니다"
            )

    # 음성 생성 버튼
    if st.button("음성 파일 생성", type="primary"):
        if not prompt or prompt == "여기에 텍스트를 입력하세요":
            st.warning("텍스트를 입력하세요.")
        else:
            with st.spinner("음성을 생성하는 중..."):
                try:
                    response = client.audio.speech.create(
                        model=model,
                        voice=selected_voice,
                        input=prompt,
                        response_format=selected_format
                    )
                    
                    audio_content = response.content
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"tts_output_{timestamp}.{selected_format}"

                    # 결과 표시
                    st.success("음성 생성 완료!")
                    
                    col5, col6 = st.columns(2)
                    with col5:
                        # 오디오 플레이어
                        b64 = base64.b64encode(audio_content).decode()
                        audio_player = f"""
                            <audio controls="controls" style="width: 100%">
                                <source src="data:audio/{selected_format};base64,{b64}" type="audio/{selected_format}">
                                Your browser does not support the audio element.
                            </audio>
                            """
                        st.markdown(audio_player, unsafe_allow_html=True)
                    
                    with col6:
                        # 다운로드 버튼
                        st.download_button(
                            label="음성 파일 다운로드",
                            data=audio_content,
                            file_name=filename,
                            mime=f"audio/{selected_format}",
                            help="생성된 음성 파일을 다운로드합니다"
                        )

                except Exception as e:
                    st.error(f"음성 생성 중 오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    render_page()