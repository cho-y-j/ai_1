import streamlit as st
import speech_recognition as sr
import os
from pydub import AudioSegment
import tempfile
import soundfile as sf
import numpy as np

def convert_audio_to_wav(input_path):
    """오디오 파일을 WAV 형식으로 변환"""
    try:
        audio = AudioSegment.from_file(input_path)
        wav_path = input_path.rsplit('.', 1)[0] + '.wav'
        audio = audio.set_channels(1)  # 모노로 변환
        audio = audio.set_frame_rate(16000)  # 샘플레이트 16kHz로 설정
        audio.export(wav_path, format='wav')
        return wav_path
    except Exception as e:
        st.error(f"오디오 변환 중 오류 발생: {str(e)}")
        raise

def convert_audio_to_text(file_path, language):
    """음성을 텍스트로 변환"""
    try:
        r = sr.Recognizer()
        # 환경 노이즈 조정
        r.dynamic_energy_threshold = True
        r.energy_threshold = 4000
        
        with sr.AudioFile(file_path) as source:
            # 오디오 데이터 조정
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = r.record(source)
            
            # 음성 인식 시도
            try:
                text = r.recognize_google(audio_data, language=language)
                return text
            except sr.UnknownValueError:
                raise Exception("음성을 인식할 수 없습니다. 다른 오디오 파일을 시도해주세요.")
            except sr.RequestError as e:
                raise Exception(f"Google API 요청 실패: {str(e)}")
    except Exception as e:
        st.error(f"음성 인식 중 오류 발생: {str(e)}")
        raise

def render_page():
    st.title("음성을 텍스트로 변환")
    
    # 세션 상태 초기화
    if 'processed_text' not in st.session_state:
        st.session_state.processed_text = None
    
    # 파일 업로드
    audio_file = st.file_uploader(
        "음성 파일을 업로드하세요 (WAV, MP3, M4A, AAC 지원)", 
        type=["wav", "mp3", "m4a", "aac"]
    )
    
    # 언어 선택
    language = st.selectbox(
        "언어 선택",
        ["한국어", "영어", "일본어"],
        index=0
    )
    
    lang_code = {
        "한국어": "ko-KR",
        "영어": "en-US",
        "일본어": "ja-JP"
    }
    
    temp_audio_path = None
    converted_wav_path = None
    
    if audio_file is not None:
        try:
            # 임시 디렉토리에 파일 저장
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.name)[1]) as temp_audio:
                temp_audio.write(audio_file.getbuffer())
                temp_audio_path = temp_audio.name
            
            # WAV로 변환
            converted_wav_path = convert_audio_to_wav(temp_audio_path)
            
            if st.button("텍스트로 변환"):
                with st.spinner("음성을 텍스트로 변환하는 중입니다..."):
                    try:
                        # 음성 인식 실행
                        text = convert_audio_to_text(converted_wav_path, lang_code[language])
                        st.session_state.processed_text = text
                        
                        st.success("변환이 완료되었습니다!")
                        st.write("변환 결과:")
                        st.write(st.session_state.processed_text)
                        
                        # 텍스트가 있을 때만 다운로드 버튼 표시
                        if st.session_state.processed_text:
                            st.download_button(
                                label="텍스트 파일 다운로드",
                                data=st.session_state.processed_text,
                                file_name="stt_output.txt",
                                mime="text/plain"
                            )
                    except Exception as e:
                        st.error(f"텍스트 변환 중 오류가 발생했습니다. 다른 파일을 시도해보세요: {str(e)}")
                        
        except Exception as e:
            st.error(f"파일 처리 중 오류가 발생했습니다: {str(e)}")
            
        finally:
            # 임시 파일 정리
            if temp_audio_path and os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
            if converted_wav_path and os.path.exists(converted_wav_path):
                os.remove(converted_wav_path)

if __name__ == "__main__":
    render_page()