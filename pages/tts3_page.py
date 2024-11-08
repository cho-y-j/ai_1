import streamlit as st
import pyttsx3
import base64
from datetime import datetime


def render_page():
    st.header("TTS (텍스트 → 음성) 변환 서비스 - 무료 버전")

    # 텍스트 입력
    prompt = st.text_area("변환할 텍스트를 입력하세요:", value="여기에 텍스트를 입력하세요", height=100)

    # 샘플 오디오 파일 경로 및 재생 (여성 목소리)
    sample_audio_path = "simple/female.mp3"

    st.subheader("샘플 음성")
    try:
        with open(sample_audio_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format="audio/mp3")
    except FileNotFoundError:
        st.warning(f"샘플 파일을 찾을 수 없습니다: {sample_audio_path}")

    # 음성 파일 형식 선택
    selected_format = st.selectbox("파일 형식을 선택하세요:", ["MP3", "WAV"]).lower()

    # 음성 파일 생성 버튼
    if st.button("음성 파일 생성"):
        if not prompt or prompt == "여기에 텍스트를 입력하세요":
            st.warning("텍스트를 입력하세요.")
        else:
            with st.spinner("음성을 생성하는 중..."):
                try:
                    # Pyttsx3 초기화 및 설정 (여성 목소리 설정)
                    engine = pyttsx3.init()
                    voices = engine.getProperty('voices')
                    for voice in voices:
                        if "female" in voice.name.lower() or "female" in voice.id.lower():
                            engine.setProperty('voice', voice.id)
                            break

                    # 파일명에 현재 시간 추가
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"tts_output_{timestamp}.{selected_format}"

                    # 음성 파일 생성
                    engine.save_to_file(prompt, filename)
                    engine.runAndWait()

                    # 생성된 음성을 브라우저에서 재생 및 다운로드 버튼 추가
                    with open(filename, "rb") as audio_file:
                        audio_bytes = audio_file.read()
                        b64 = base64.b64encode(audio_bytes).decode()
                        audio_player = f"""
                            <audio controls="controls" style="width: 100%">
                                <source src="data:audio/{selected_format};base64,{b64}" type="audio/{selected_format}">
                                Your browser does not support the audio element.
                            </audio>
                            """
                        st.markdown(audio_player, unsafe_allow_html=True)

                        # 다운로드 버튼 추가
                        st.download_button(
                            label="음성 파일 다운로드",
                            data=audio_bytes,
                            file_name=filename,
                            mime=f"audio/{selected_format}"
                        )

                    st.success("음성 파일 생성이 완료되었습니다!")
                except Exception as e:
                    st.error("음성 파일을 생성하는 데 오류가 발생했습니다.")
                    st.write(e)

# Streamlit 페이지 실행
def main():
    render_page()

if __name__ == "__main__":
    main()
