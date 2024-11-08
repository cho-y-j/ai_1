import streamlit as st
from openai import OpenAI
import os
from typing import Literal
from datetime import datetime

def init_session_state():
    """Initialize session state variables"""
    if 'transcript_text' not in st.session_state:
        st.session_state['transcript_text'] = ""
    if 'summary_text' not in st.session_state:
        st.session_state['summary_text'] = ""
    if 'transcript_edited' not in st.session_state:
        st.session_state['transcript_edited'] = ""
    if 'summary_edited' not in st.session_state:
        st.session_state['summary_edited'] = ""
    if 'show_transcript' not in st.session_state:
        st.session_state['show_transcript'] = False
    if 'show_summary' not in st.session_state:
        st.session_state['show_summary'] = False

def get_language_code(language: str) -> str:
    """Get ISO language code from language name"""
    return {
        "한국어": "ko",
        "영어": "en",
        "스페인어": "es",
        "프랑스어": "fr",
        "독일어": "de",
        "중국어": "zh",
        "일본어": "ja"
    }.get(language, "ko")  # 기본값을 'ko'로 변경

def format_timestamps(words: list) -> str:
    """Format timestamp data into readable text"""
    formatted_text = []
    for word in words:
        start = float(word.start)
        end = float(word.end)
        formatted_text.append(
            f"[{start:.2f} - {end:.2f}] {word.text}"
        )
    return "\n".join(formatted_text)

def process_audio(
    client: OpenAI,
    audio_file,
    transcription_type: Literal["번역", "타임스탬프 적용"],
    language: str
) -> str:
    """Process audio file based on selected options"""
    try:
        language_code = get_language_code(language)
        
        # 한국어 음성을 영어로 번역하는 경우
        if transcription_type == "번역" and language == "한국어":
            response = client.audio.translations.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        # 타임스탬프가 필요한 경우
        elif transcription_type == "타임스탬프 적용":
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["word"],
                language=language_code
            )
            return format_timestamps(response.words)
        # 일반 전사의 경우
        else:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text",
                language=language_code
            )
        
        return response.text if hasattr(response, 'text') else str(response)

    except Exception as e:
        st.error(f"음성 처리 중 오류가 발생했습니다: {str(e)}")
        return ""

def generate_summary(client: OpenAI, transcript: str, prompt: str) -> str:
    """Generate summary using OpenAI Chat API"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that specializes in summarizing meeting minutes in Korean."},
                {"role": "user", "content": f"{prompt}\n\n{transcript}"}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"요약 생성 중 오류가 발생했습니다: {str(e)}")
        return ""

def render_download_buttons(transcript: str = None, summary: str = None):
    """Render download buttons for transcript and summary"""
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if transcript:
            st.download_button(
                label="전체 텍스트 다운로드",
                data=transcript,
                file_name=f"transcript_{current_time}.txt",
                mime="text/plain",
                key=f"download_transcript_{current_time}"
            )
    
    with col2:
        if summary:
            st.download_button(
                label="회의록 요약본 다운로드",
                data=summary,
                file_name=f"summary_{current_time}.txt",
                mime="text/plain",
                key=f"download_summary_{current_time}"
            )

def render_page():
    """Main page rendering function"""
    st.header("STT (음성 → 텍스트) 및 회의록 생성 서비스")
    
    # Initialize session state
    init_session_state()
    
    # Setup OpenAI client
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # File uploader
    uploaded_file = st.file_uploader(
        "음성 파일을 업로드하세요 (MP3, WAV, M4A, MP4, MPEG, MPGA, WEBM)",
        type=["mp3", "wav", "m4a", "mp4", "mpeg", "mpga", "webm"]
    )
    
    # Language selection with Korean as default
    language = st.selectbox(
        "변환할 언어를 선택하세요:",
        ("한국어", "영어", "스페인어", "프랑스어", "독일어", "중국어", "일본어"),
        index=0  # 한국어를 기본값으로 설정
    )
    
    # Transcription type selection
    transcription_type = st.radio(
        "변환 옵션을 선택하세요:",
        ("번역", "타임스탬프 적용"),
        help="번역: 다른 언어를 영어로 번역 / 타임스탬프: 음성을 텍스트로 변환하며 시간 정보 포함"
    )
    
    # Process audio file
    if uploaded_file and st.button("텍스트로 변환"):
        with st.spinner("음성을 변환하는 중..."):
            st.session_state['transcript_text'] = process_audio(
                client,
                uploaded_file,
                transcription_type,
                language
            )
            if st.session_state['transcript_text']:
                st.session_state['transcript_edited'] = st.session_state['transcript_text']
                st.session_state['show_transcript'] = True

    # Display and edit transcript
    if st.session_state['show_transcript']:
        st.subheader("변환된 텍스트")
        st.session_state['transcript_edited'] = st.text_area(
            "회의록 텍스트 (수정 가능):",
            value=st.session_state['transcript_edited'],
            height=200,
            key="transcript_editor"
        )
        
        render_download_buttons(st.session_state['transcript_edited'])
    
        # Summary generation
        st.subheader("회의록 요약 프롬프트 입력")
        default_prompt = (
            "다음 회의록을 회사 회의용 형식으로 요약하세요. "
            "주요 논의 사항, 결정된 사항, 후속 작업을 포함해 정리해 주세요."
        )
        user_prompt = st.text_area(
            "프롬프트 입력",
            value=default_prompt,
            height=100
        )
        
        if st.button("요약본 생성", key="generate_summary"):
            with st.spinner("회의록 요약본을 생성하는 중..."):
                st.session_state['summary_text'] = generate_summary(
                    client,
                    st.session_state['transcript_edited'],
                    user_prompt
                )
                if st.session_state['summary_text']:
                    st.session_state['summary_edited'] = st.session_state['summary_text']
                    st.session_state['show_summary'] = True

    # Display and edit summary
    if st.session_state['show_summary']:
        st.session_state['summary_edited'] = st.text_area(
            "요약본 (수정 가능):",
            value=st.session_state['summary_edited'],
            height=150,
            key="summary_editor"
        )
        render_download_buttons(
            st.session_state['transcript_edited'],
            st.session_state['summary_edited']
        )
    
    # Reset button with confirmation
    if st.button("처음으로"):
        if st.session_state['transcript_text'] or st.session_state['summary_text']:
            if st.checkbox("정말 처음으로 돌아가시겠습니까? 모든 내용이 삭제됩니다."):
                for key in st.session_state.keys():
                    st.session_state[key] = ""
                st.experimental_rerun()