from groq import Groq
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"


def explain_report(report_text: str, language: str = 'en') -> str:
    """
    Takes raw lab report text and returns a plain language explanation.
    Supports English ('en') and Urdu ('ur').
    """
    if language == 'ur':
        system_msg = "آپ ایک دوستانہ طبی معاون ہیں جو پاکستانی مریضوں کو ان کی لیب رپورٹس سمجھنے میں مدد کرتے ہیں۔ ہمیشہ اردو میں جواب دیں۔ پرسکون، واضح اور معاون رہیں۔ تشخیص نہ کریں — صرف وضاحت کریں۔"
        user_msg = f"""اس لیب رپورٹ کو سادہ اردو میں سمجھائیں جو ایک عام آدمی سمجھ سکے۔
ہر ٹیسٹ کی قدر کے لیے:
- بتائیں کہ یہ نارمل ہے یا غیر نارمل
- سادہ زبان میں وضاحت کریں
- بتائیں کہ مریض کو فکر کرنی چاہیے یا نہیں

لیب رپورٹ:
{report_text}"""
    else:
        system_msg = "You are a friendly medical assistant helping Pakistani patients understand their lab reports. Always be calm, clear, and supportive. Never diagnose — only explain."
        user_msg = f"""Explain this lab report in simple English that a non-doctor can understand.
For each test value:
- State whether it is NORMAL or ABNORMAL
- Explain what the value means in plain language
- Mention if the patient should be concerned

Lab Report:
{report_text}"""

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
    """
    Answers a user's follow-up question about their specific report.
    Supports English ('en') and Urdu ('ur').
    """
    if language == 'ur':
        system_msg = "آپ ایک مددگار طبی معاون ہیں۔ لیب رپورٹس کے بارے میں سوالات کا جواب اردو میں واضح اور سادہ انداز میں دیں۔ تشخیص نہ کریں۔"
    else:
        system_msg = "You are a helpful medical assistant. Answer questions about lab reports clearly and simply. Do not diagnose. If the question is outside the scope of the report, say so politely."

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
    """
    Returns: {
        'score': 72, 'level': 'High', 'color': 'red',
        'alerts': ['High glucose', 'Low hemoglobin'],
        'positives': ['WBC count normal']
    }
    """
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a medical risk assessment AI. You only respond with valid JSON. No markdown, no explanation, no extra text."
                },
                {
                    "role": "user",
                    "content": f"""Analyze this lab report and return a JSON risk summary.

Rules:
- score: integer 0-100 (0=perfect, 100=critical)
- level: "Low" (0-25), "Medium" (26-50), "High" (51-75), "Critical" (76-100)
- color: "green" for Low, "orange" for Medium, "red" for High or Critical
- alerts: list of short strings for abnormal values e.g. ["High glucose", "Low hemoglobin"]
- positives: list of short strings for normal values e.g. ["WBC count normal", "Platelets healthy"]
- If all normal: score=10, level="Low", color="green", alerts=[], positives=["All values normal"]

Return ONLY this JSON format:
{{"score": 72, "level": "High", "color": "red", "alerts": ["High glucose"], "positives": ["WBC normal"]}}

Lab Report:
{report_text}"""
                }
            ],
            temperature=0.1,
            max_tokens=300,
        )

        raw = response.choices[0].message.content.strip()
        raw = re.sub(r"```json|```", "", raw).strip()
        result = json.loads(raw)

        score = max(0, min(100, int(result.get("score", 10))))
        level = result.get("level", "Low")
        alerts = result.get("alerts", [])
        positives = result.get("positives", [])

        if level not in ["Low", "Medium", "High", "Critical"]:
            level = "Low"

        color_map = {"Low": "green", "Medium": "orange", "High": "red", "Critical": "red"}
        color = color_map.get(level, "green")

        return {"score": score, "level": level, "color": color,
                "alerts": alerts, "positives": positives}

    except Exception as e:
        return {"score": 0, "level": "Low", "color": "green",
                "alerts": [f"Could not parse risk: {str(e)}"], "positives": []}


def extract_key_values(report_text: str) -> dict:
    """
    Extracts numeric health values from report text.
    Used by the Health Trends page.
    Returns: {'Glucose': 105.0, 'Hemoglobin': 11.2, 'WBC': 6.5, ...}
    """
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a medical data extraction AI. You only respond with valid JSON. No markdown, no explanation, no extra text."
                },
                {
                    "role": "user",
                    "content": f"""Extract all numeric health values from this lab report.

Return ONLY a JSON object with test names as keys and numeric values as values.
Use standard names: Glucose, Hemoglobin, WBC, Platelets, Creatinine, Cholesterol, HbA1c, Sodium, Potassium, ALT, AST, Bilirubin, Urea

Example output:
{{"Glucose": 105.0, "Hemoglobin": 11.2, "WBC": 6.5, "Platelets": 250.0}}

If a value cannot be found, do not include it.
Return ONLY the JSON object, nothing else.

Lab Report:
{report_text}"""
                }
            ],
            temperature=0.1,
            max_tokens=256,
        )

        raw = response.choices[0].message.content.strip()
        raw = re.sub(r"```json|```", "", raw).strip()
        result = json.loads(raw)

        # Keep only numeric values
        return {k: float(v) for k, v in result.items() if isinstance(v, (int, float))}

    except Exception as e:
        return {}
