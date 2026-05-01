from groq import Groq
import os, json, re

# ── Colab: read key from Colab Secrets (userdata) ──────────────────────────
try:
    from google.colab import userdata
    GROQ_API_KEY = userdata.get('GROQ_API_KEY')
except Exception:
    # Fallback: read from environment variable (local / .env)
    from dotenv import load_dotenv
    load_dotenv()
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')

client = Groq(api_key=GROQ_API_KEY)
MODEL = 'llama-3.3-70b-versatile'


def _chat(prompt: str) -> str:
    """Internal helper — sends a single prompt to Groq and returns the reply."""
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{'role': 'user', 'content': prompt}],
        max_tokens=1024,
        temperature=0.3,
    )
    return resp.choices[0].message.content


# ■■ FUNCTION 1 — Called by Tech 2 ■■■■■■■■■■■■■■■■■■
def explain_report(report_text: str, language: str = 'en') -> str:
    """
    Returns a plain-language explanation of the lab report.

    Args:
        report_text: Raw text extracted from the uploaded PDF / image.
        language:    'en' for English, 'ur' for Urdu.

    Returns:
        str — formatted explanation with NORMAL/ABNORMAL labels per test.
    """
    if not report_text.strip():
        return 'No report text found. Please upload a clearer file.'

    lang = 'Respond in simple Urdu.' if language == 'ur' else 'Respond in simple English.'
    prompt = f'''You are a medical assistant for Pakistani patients. {lang}
For each test: say NORMAL or ABNORMAL and explain in 1-2 sentences.
End with overall summary. Always end with:
Please consult your doctor for medical advice.

Lab Report:
{report_text}'''
    return _chat(prompt)


# ■■ FUNCTION 2 — Called by Tech 4 ■■■■■■■■■■■■■■■■■■
def chat_with_report(report_text: str, question: str, language: str = 'en') -> str:
    """
    Answers a user question strictly based on the uploaded lab report.

    Args:
        report_text: Raw text of the report.
        question:    User's natural-language question.
        language:    'en' or 'ur'.

    Returns:
        str — answer grounded in the report.
    """
    if not report_text.strip():
        return 'Please upload a report first.'

    lang = 'Respond in simple Urdu.' if language == 'ur' else 'Respond in simple English.'
    prompt = f'''You are a medical assistant. {lang}
Answer ONLY based on this report. Recommend doctor for serious concerns.

Lab Report:
{report_text}

Question: {question}'''
    return _chat(prompt)


# ■■ FUNCTION 3 — Called by Tech 2 via risk_scorer ■■
def summarize_risk(report_text: str) -> dict:
    """
    Produces a structured risk assessment of the lab report.

    Args:
        report_text: Raw text of the report.

    Returns:
        dict with keys:
            score     (int  0-100)
            level     (str  'Low' | 'Medium' | 'High' | 'Critical')
            color     (str  'green' | 'orange' | 'red' | 'darkred')
            alerts    (list[str]  — abnormal findings)
            positives (list[str]  — normal findings)
    """
    if not report_text.strip():
        return {'score': 0, 'level': 'Unknown', 'color': 'gray', 'alerts': [], 'positives': []}

    prompt = f'''Analyze this lab report. Return ONLY raw JSON, no markdown, no extra text.
Format exactly:
{{"score":0-100,"level":"Low|Medium|High|Critical","alerts":["abnormal finding 1"],"positives":["normal finding 1"]}}

Lab Report:
{report_text}'''

    raw = re.sub(r'```json|```', '', _chat(prompt)).strip()
    try:
        r = json.loads(raw)
        s = int(r.get('score', 50))
        return {
            'score':     s,
            'level':     r.get('level', 'Medium'),
            'color':     'green'   if s < 30 else
                         'orange'  if s < 60 else
                         'red'     if s < 85 else 'darkred',
            'alerts':    r.get('alerts',    []),
            'positives': r.get('positives', []),
        }
    except Exception:
        return {'score': 50, 'level': 'Medium', 'color': 'orange',
                'alerts': ['Could not parse report'], 'positives': []}


# ■■ FUNCTION 4 — Called by Tech 3 ■■■■■■■■■■■■■■■■■■
def extract_key_values(report_text: str) -> dict:
    """
    Extracts numeric test results as a key-value dict.

    Args:
        report_text: Raw text of the report.

    Returns:
        dict — e.g. {"Glucose": 110, "Hemoglobin": 13.5}
    """
    if not report_text.strip():
        return {}

    prompt = f'''Extract numeric test values from the lab report.
Return ONLY raw JSON, no markdown, no extra text.
Example: {{"Glucose":110,"Hemoglobin":13.5}}

Lab Report:
{report_text}'''

    raw = re.sub(r'```json|```', '', _chat(prompt)).strip()
    try:
        return json.loads(raw)
    except Exception:
        return {}
