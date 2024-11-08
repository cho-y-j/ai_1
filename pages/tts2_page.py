import streamlit as st
from gtts import gTTS
import pyttsx3
import tempfile
import os
from io import BytesIO
from datetime import datetime
import subprocess

def get_pyttsx3_voices():
    """사용 가능한 로컬 음성 목록 가져오기"""
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    return {f"local_{i}": voice for i, voice in enumerate(voices)}

def text_to_speech_local(text, selected_voice, rate=150):
    """pyttsx3를 사용하여 로컬 TTS 변환 후 파일로 저장"""
    engine = pyttsx3.init()
    voices = get_pyttsx3_voices()
    
    # 음성 설정
    engine.setProperty('voice', voices[selected_voice].id)
    engine.setProperty('rate', rate)
    
    # 임시 파일에 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
        temp_filename = temp_file.name
    engine.save_to_file(text, temp_filename)
    engine.runAndWait()
    
    # ffmpeg를 사용하여 파일 변환 (호환성 문제 해결)
    converted_filename = temp_filename.replace('.wav', '_converted.mp3')
    try:
        subprocess.run(
            ['ffmpeg', '-i', temp_filename, converted_filename],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError as e:
        st.error("ffmpeg 변환 중 오류가 발생했습니다.")
        st.write(e.stderr.decode())
        return None
    finally:
        os.remove(temp_filename)  # 원본 임시 파일 삭제

    return converted_filename

def text_to_speech_gtts(text, lang='ko'):
    """Google TTS를 사용하여 온라인 TTS 변환 후 메모리로 반환"""
    tts = gTTS(text=text, lang=lang, slow=False)
    audio_bytes = BytesIO()
    tts.write_to_fp(audio_bytes)
    return audio_bytes.getvalue()

def render_page():
    st.title("무료 TTS (텍스트 → 음성) 변환 서비스")
    
    # 서비스 선택
    service_type = st.radio(
        "TTS 서비스 선택:",
        ["Google TTS (온라인)", "Local TTS (오프라인)"],
        help="온라인 서비스는 인터넷 연결이 필요하며 더 자연스러운 음성을 제공합니다."
    )
    
    # Google TTS 언어 옵션
    gtts_languages = {
        "한국어": "ko",
        "영어": "en",
        "일본어": "ja",
        "중국어": "zh-CN",
        "스페인어": "es",
        "프랑스어": "fr",
        "독일어": "de"
    }
    
    # 텍스트 입력
    text_input = st.text_area(
        "변환할 텍스트를 입력하세요:",
        value="안녕하세요, 반갑습니다.",
        height=150
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if service_type == "Google TTS (온라인)":
            selected_lang = st.selectbox(
                "언어 선택:",
                list(gtts_languages.keys())
            )
            lang_code = gtts_languages[selected_lang]
        else:
            voices = get_pyttsx3_voices()
            selected_voice = st.selectbox(
                "음성 선택:",
                [f"local_{i}" for i in range(len(voices))]
            )
            
            # 음성 속도 조절
            rate = st.slider(
                "음성 속도:",
                min_value=50,
                max_value=300,
                value=150,
                step=10,
                help="숫자가 클수록 더 빠른 속도로 읽습니다."
            )
    
    if st.button("음성 변환 시작"):
        if not text_input.strip():
            st.warning("텍스트를 입력해주세요.")
            return
            
        try:
            with st.spinner("음성을 생성하는 중..."):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                if service_type == "Google TTS (온라인)":
                    try:
                        audio_bytes = text_to_speech_gtts(text_input, lang_code)
                        output_format = "mp3"
                    except Exception as e:
                        st.error(f"Google TTS 변환 중 오류가 발생했습니다: {str(e)}")
                        st.info("인터넷 연결을 확인하거나 Local TTS를 시도해보세요.")
                        return
                else:
                    try:
                        temp_file = text_to_speech_local(text_input, selected_voice, rate)
                        if temp_file:
                            with open(temp_file, 'rb') as f:
                                audio_bytes = f.read()
                            output_format = "mp3"
                            os.remove(temp_file)  # 변환된 임시 파일 삭제
                        else:
                            st.error("로컬 TTS 파일 변환에 실패했습니다.")
                            return
                    except Exception as e:
                        st.error(f"Local TTS 변환 중 오류가 발생했습니다: {str(e)}")
                        return
                
                # 오디오 재생기 표시
                st.audio(audio_bytes, format=f'audio/{output_format}')
                
                # 다운로드 버튼
                st.download_button(
                    label="음성 파일 다운로드",
                    data=audio_bytes,
                    file_name=f"tts_output_{timestamp}.{output_format}",
                    mime=f"audio/{output_format}"
                )
                
                st.success("음성 변환이 완료되었습니다!")
                
        except Exception as e:
            st.error(f"음성 변환 중 오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    render_page()
