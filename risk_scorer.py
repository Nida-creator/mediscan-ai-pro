import streamlit as st
from ai_engine import summarize_risk


def show_risk_score(report_text: str):
    """
    Renders the full risk score UI inside a Streamlit page.

    Args:
        report_text: Raw text of the uploaded lab report.
    """
    with st.spinner('Calculating health risk score...'):
        risk = summarize_risk(report_text)

    score  = risk['score']
    level  = risk['level']
    color  = risk['color']

    # Background / foreground colour map
    cmap = {
        'green':   ('#E1F5EE', '#0F6E56'),
        'orange':  ('#FAEEDA', '#633806'),
        'red':     ('#FCEBEB', '#791F1F'),
        'darkred': ('#F7C1C1', '#501313'),
        'gray':    ('#F1EFE8', '#5F5E5A'),
    }
    bg, fg = cmap.get(color, ('#F1EFE8', '#5F5E5A'))

    st.subheader('🩺 Health Risk Score')

    c1, c2 = st.columns([1, 2])

    with c1:
        st.markdown(
            f"""
            <div style="background:{bg}; border-radius:12px; padding:24px; text-align:center;">
                <p style="font-size:40px; font-weight:700; color:{fg}; margin:0">{score}<span style="font-size:20px">/100</span></p>
                <p style="color:{fg}; margin:4px 0 0 0; font-weight:600">{level} Risk</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(f'**Risk Level: {level}**')
        st.progress(score / 100)
        st.caption(f'Score: {score} / 100')

    st.divider()

    c3, c4 = st.columns(2)

    with c3:
        st.markdown('### ⚠️ Needs Attention')
        if risk['alerts']:
            for a in risk['alerts']:
                st.error(f'🔴 {a}')
        else:
            st.success('No critical values found!')

    with c4:
        st.markdown('### ✅ Looking Good')
        if risk['positives']:
            for g in risk['positives']:
                st.success(f'🟢 {g}')
        else:
            st.info('No positives listed.')

    st.caption('⚕️ Educational tool only. Always consult a qualified doctor.')
