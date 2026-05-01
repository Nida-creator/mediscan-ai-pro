"""
MediScan AI Pro — Main Streamlit Entry Point
Run on Google Colab with:
    !streamlit run app.py &
    from pyngrok import ngrok; print(ngrok.connect(8501))
"""

import streamlit as st

# ── Page configuration (MUST be first Streamlit call) ──────────────────────
st.set_page_config(
    page_title='MediScan AI Pro',
    page_icon='🩺',
    layout='wide',
    initial_sidebar_state='expanded',
)

# ── Imports after page config ───────────────────────────────────────────────
from ai_engine import explain_report, chat_with_report, extract_key_values
from risk_scorer import show_risk_score
import pdfplumber
import io

# ───────────────────────────────────────────────────────────────────────────
# Helper — extract text from uploaded file
# ───────────────────────────────────────────────────────────────────────────
def extract_text(uploaded_file) -> str:
    """Returns plain text from a PDF or TXT upload."""
    if uploaded_file is None:
        return ''
    if uploaded_file.type == 'application/pdf':
        with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
            return '\n'.join(page.extract_text() or '' for page in pdf.pages)
    # Plain text fallback
    return uploaded_file.read().decode('utf-8', errors='ignore')


# ───────────────────────────────────────────────────────────────────────────
# Sidebar — navigation + upload
# ───────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image('https://img.icons8.com/color/96/stethoscope.png', width=64)
    st.title('MediScan AI Pro')
    st.caption('Pak Angels Gen AI Hackathon')
    st.divider()

    page = st.radio(
        'Navigate',
        ['🏠 Home', '📄 Report Explanation', '⚠️ Risk Score', '💬 Chat', '📊 Key Values'],
        label_visibility='collapsed',
    )

    st.divider()
    language = st.selectbox('Language / زبان', ['English', 'اردو'])
    lang_code = 'ur' if language == 'اردو' else 'en'

    st.divider()
    uploaded_file = st.file_uploader('Upload Lab Report (PDF / TXT)', type=['pdf', 'txt'])
    report_text = extract_text(uploaded_file) if uploaded_file else ''

    if report_text:
        st.success('✅ Report loaded!')
    else:
        st.info('Upload a report to get started.')


# ───────────────────────────────────────────────────────────────────────────
# Pages
# ───────────────────────────────────────────────────────────────────────────

# ── Home ────────────────────────────────────────────────────────────────────
if page == '🏠 Home':
    st.title('🩺 MediScan AI Pro')
    st.subheader('Your AI-Powered Lab Report Assistant')
    st.markdown(
        """
        MediScan AI Pro helps Pakistani patients understand their lab reports in simple language — in English or Urdu.

        **What you can do:**
        - 📄 Get a plain-English (or Urdu) explanation of every test
        - ⚠️ See an overall Health Risk Score with colour-coded alerts
        - 💬 Chat with your report — ask any question
        - 📊 View extracted numeric values at a glance
        """
    )

    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric('Model', 'LLaMA 3.3 70B')
    col2.metric('Powered by', 'Groq')
    col3.metric('Languages', '2')
    col4.metric('Risk Levels', '4')

    st.divider()
    st.info('👈 Upload your lab report in the sidebar to begin.')


# ── Report Explanation ───────────────────────────────────────────────────────
elif page == '📄 Report Explanation':
    st.title('📄 Report Explanation')

    if not report_text:
        st.warning('Please upload a lab report from the sidebar first.')
    else:
        if st.button('🔍 Explain My Report', type='primary'):
            with st.spinner('Analysing your report...'):
                result = explain_report(report_text, language=lang_code)
            st.markdown(result)


# ── Risk Score ───────────────────────────────────────────────────────────────
elif page == '⚠️ Risk Score':
    st.title('⚠️ Health Risk Score')

    if not report_text:
        st.warning('Please upload a lab report from the sidebar first.')
    else:
        if st.button('📊 Calculate Risk Score', type='primary'):
            show_risk_score(report_text)


# ── Chat ─────────────────────────────────────────────────────────────────────
elif page == '💬 Chat':
    st.title('💬 Chat With Your Report')

    if not report_text:
        st.warning('Please upload a lab report from the sidebar first.')
    else:
        # Keep chat history in session state
        if 'messages' not in st.session_state:
            st.session_state.messages = []

        # Render previous messages
        for msg in st.session_state.messages:
            with st.chat_message(msg['role']):
                st.markdown(msg['content'])

        # New user input
        question = st.chat_input('Ask anything about your report…')
        if question:
            st.session_state.messages.append({'role': 'user', 'content': question})
            with st.chat_message('user'):
                st.markdown(question)

            with st.chat_message('assistant'):
                with st.spinner('Thinking…'):
                    answer = chat_with_report(report_text, question, language=lang_code)
                st.markdown(answer)
            st.session_state.messages.append({'role': 'assistant', 'content': answer})


# ── Key Values ────────────────────────────────────────────────────────────────
elif page == '📊 Key Values':
    st.title('📊 Extracted Key Values')

    if not report_text:
        st.warning('Please upload a lab report from the sidebar first.')
    else:
        if st.button('🔢 Extract Values', type='primary'):
            with st.spinner('Extracting numeric values…'):
                values = extract_key_values(report_text)

            if values:
                st.success(f'Found {len(values)} test values.')
                cols = st.columns(3)
                for i, (test, val) in enumerate(values.items()):
                    cols[i % 3].metric(label=test, value=val)
            else:
                st.error('Could not extract values. Try a clearer PDF.')
