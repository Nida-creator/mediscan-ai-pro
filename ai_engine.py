from groq import Groq
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()

import re

def clean_report_text(text: str) -> str:
    """Remove non-English characters and clean up report text before sending to AI."""
    # Remove Chinese, Malay and other non-Latin characters
    text = re.sub(r'[\u4e00-\u9fff]+', '', text)  # Remove Chinese
    text = re.sub(r'[\u0600-\u06ff]+', '', text)  # Remove Arabic
    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    # Remove garbled lines (lines with no letters)
    lines = text.split('\n')
    clean_lines = [l for l in lines if re.search(r'[a-zA-Z]', l)]
    return '\n'.join(clean_lines).strip()


client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"


def explain_report(report_text: str, language: str = 'en') -> str:
    if language == 'ur':
        system_msg = "آپ ایک دوستانہ طبی معاون ہیں۔ ہمیشہ اردو میں جواب دیں۔ تشخیص نہ کریں۔"
        user_msg = f"اس لیب رپورٹ کو سادہ اردو میں سمجھائیں:\n{report_text}"
    else:
        system_msg = "You are a friendly medical assistant helping Pakistani patients understand their lab reports. Never diagnose — only explain. Do NOT use **, *, #, or numbered lists."
        user_msg = f"""Explain this lab report clearly. Follow this exact format:

SECTION: Blood Count
- Hemoglobin: ABNORMAL — Low at 8.0. This means fewer red blood cells carrying oxygen.
- WBC: NORMAL — Good immune defense.

SECTION: Lipid Profile
- Cholesterol: NORMAL — Heart risk is low.

Rules:
- Start each group with SECTION: GroupName on its own line
- Each value on its own line starting with -
- Keep each line short and simple
- End with SECTION: Summary and 2-3 sentences overall
- No asterisks, no numbers, no markdown

Lab Report:\n{report_text}"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.3,
            max_tokens=1024,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error getting explanation: {str(e)}"


def chat_with_report(report_text: str, question: str, language: str = 'en') -> str:
    if language == 'ur':
        system_msg = (
            "آپ ایک ذہین اور دوستانہ AI ڈاکٹر ہیں جو پاکستانی مریضوں کی مدد کرتے ہیں۔ "
            "آپ کے پاس مریض کی لیب رپورٹ موجود ہے۔ "
            "آپ ہر طرح کے صحت سے متعلق سوالات کا جواب دے سکتے ہیں۔ "
            "ہمیشہ اردو میں جواب دیں۔ تشخیص نہ کریں لیکن مفید مشورہ ضرور دیں۔"
        )
    else:
        system_msg = (
            "You are a smart, friendly AI health assistant helping Pakistani patients. "
            "You have access to the patient's lab report. "
            "Answer ANY health question: diet advice (eggs, meat, sugar), exercise, "
            "lifestyle changes, what abnormal values mean for daily life, general health tips. "
            "Be conversational and warm like a knowledgeable doctor friend. "
            "Give useful specific advice. Never give a formal diagnosis."
        )

    report_context = f"Patient Lab Report:\n{report_text}\n\n" if report_text else ""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": f"{report_context}Patient question: {question}"}
            ],
            temperature=0.5,
            max_tokens=600,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error answering question: {str(e)}"

def summarize_risk(report_text: str) -> dict:
    default = {"score": 10, "level": "Low", "color": "green", "alerts": [], "positives": ["All values appear normal"]}
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a medical risk AI. Respond ONLY with a valid JSON object. No markdown, no text, no explanation. Just the JSON."
                },
                {
                    "role": "user",
                    "content": f"""Analyze this lab report. Return ONLY this JSON:
{{"score": 72, "level": "High", "color": "red", "alerts": ["High glucose"], "positives": ["WBC normal"]}}

Rules:
- score: 0-100
- level: Low(0-25), Medium(26-50), High(51-75), Critical(76-100)
- color: green/orange/red
- alerts: abnormal values
- positives: normal values

Lab Report:
{report_text}"""
                }
            ],
            temperature=0.1,
            max_tokens=300,
        )

        raw = response.choices[0].message.content.strip()
        raw = re.sub(r"```json|```", "", raw).strip()

        if not raw:
            return default

        result = json.loads(raw)
        score = max(0, min(100, int(result.get("score", 10))))
        level = result.get("level", "Low")
        if level not in ["Low", "Medium", "High", "Critical"]:
            level = "Low"
        color_map = {"Low": "green", "Medium": "orange", "High": "red", "Critical": "red"}

        return {
            "score": score,
            "level": level,
            "color": color_map.get(level, "green"),
            "alerts": result.get("alerts", []),
            "positives": result.get("positives", [])
        }

    except Exception as e:
        # Fallback — try to extract score from explanation text
        try:
            fallback = explain_report(report_text)
            if any(word in fallback.lower() for word in ['abnormal', 'high', 'low', 'critical']):
                return {"score": 60, "level": "Medium", "color": "orange",
                        "alerts": ["Some values need attention"], "positives": []}
            else:
                return {"score": 20, "level": "Low", "color": "green",
                        "alerts": [], "positives": ["Values appear normal"]}
        except:
            return {"score": 30, "level": "Low", "color": "green",
                    "alerts": [], "positives": ["Report processed successfully"]}


def extract_key_values(report_text: str) -> dict:
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a medical data extraction AI. Respond ONLY with valid JSON. No markdown, no text."
                },
                {
                    "role": "user",
                    "content": f"""Extract numeric health values from this report.
Return ONLY JSON like: {{"Glucose": 105.0, "Hemoglobin": 11.2, "WBC": 6.5}}
Lab Report:\n{report_text}"""
                }
            ],
            temperature=0.1,
            max_tokens=256,
        )
        raw = response.choices[0].message.content.strip()
        raw = re.sub(r"```json|```", "", raw).strip()
        if not raw:
            return {}
        result = json.loads(raw)
        return {k: float(v) for k, v in result.items() if isinstance(v, (int, float))}
    except Exception:
        return {}
