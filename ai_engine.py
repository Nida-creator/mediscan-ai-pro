from groq import Groq
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"


def explain_report(report_text: str, language: str = 'en') -> str:
    if language == 'ur':
        system_msg = "آپ ایک دوستانہ طبی معاون ہیں۔ ہمیشہ اردو میں جواب دیں۔ تشخیص نہ کریں۔"
        user_msg = f"اس لیب رپورٹ کو سادہ اردو میں سمجھائیں:\n{report_text}"
    else:
        system_msg = "You are a friendly medical assistant helping Pakistani patients understand their lab reports. Never diagnose — only explain."
        user_msg = f"""Explain this lab report in simple English.
For each value: state NORMAL or ABNORMAL, explain what it means, mention if concerning.
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
        system_msg = "آپ ایک مددگار طبی معاون ہیں۔ اردو میں جواب دیں۔ تشخیص نہ کریں۔"
    else:
        system_msg = "You are a helpful medical assistant. Answer questions about lab reports clearly. Do not diagnose."

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": f"Lab Report:\n{report_text}\n\nQuestion:\n{question}"}
            ],
            temperature=0.3,
            max_tokens=512,
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
        return {"score": 0, "level": "Low", "color": "green",
                "alerts": [f"Could not parse risk: {str(e)}"], "positives": []}


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
