"""
MediScan AI Pro — Flask Backend
Connects all AI functions to the HTML frontend.
"""

from flask import Flask, render_template, request, jsonify, session
import os, json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "mediscan-hackathon-2026-secret")

# ── Jinja2 avatar filter ──────────────────────────────────────────────────────
AVATARS = {
    'Myself':'🧑','Father':'👨','Mother':'👩','Son':'👦','Daughter':'👧',
    'Brother':'👱','Sister':'👱‍♀️','Husband':'👨','Wife':'👩',
    'Grandfather':'👴','Grandmother':'👵','Other':'👤'
}
@app.template_filter('avatar')
def avatar_filter(relation):
    return AVATARS.get(relation, '👤')
UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ── Import AI functions ───────────────────────────────────────────────────────
try:
    from ai_engine import explain_report, chat_with_report, summarize_risk, extract_key_values
    from report_parser import extract_text
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

# ── Demo fallbacks ────────────────────────────────────────────────────────────
def demo_explain(text, lang='en'):
    return "Your Hemoglobin is 11.2 g/dL — slightly below normal (12–16). Your Glucose is 105 mg/dL — borderline high. WBC count 6.5 is within the healthy range. Please consult your doctor for medical advice."

def demo_risk(text):
    return {'score': 72, 'level': 'Medium', 'color': 'orange',
            'alerts': ['Low hemoglobin detected', 'Glucose borderline high'],
            'positives': ['WBC count normal', 'Platelets in healthy range']}

def demo_chat(text, question, lang='en'):
    return f"Based on your report: {question} — This is a demo response. Connect ai_engine.py for real answers."

def demo_keys(text):
    return {'Glucose': 105, 'Hemoglobin': 11.2, 'WBC': 6.5, 'Platelets': 250}

def demo_extract(file):
    return "Hemoglobin: 11.2 | Glucose: 105 | WBC: 6.5 | Platelets: 250"

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def dashboard():
    name = session.get('user_name', '')
    stats = session.get('stats', {'total': 0, 'last_score': '—', 'this_month': 0})
    recent = session.get('recent_reports', [])
    return render_template('dashboard.html', name=name, stats=stats, recent=recent)

@app.route('/set-name', methods=['POST'])
def set_name():
    data = request.get_json()
    session['user_name'] = data.get('name', 'User')
    return jsonify({'ok': True})

@app.route('/scan')
def scan():
    return render_template('scan.html')

@app.route('/upload', methods=['POST'])
def upload():
    print("DEBUG active_member in session:", session.get('active_member', 'NOT FOUND'))
    print("DEBUG family file exists:", os.path.exists(FAMILY_FILE))
    print("DEBUG all session keys:", list(session.keys()))
    import logging
    logging.basicConfig(level=logging.DEBUG)
    logging.debug(f"Files in request: {list(request.files.keys())}")
    logging.debug(f"Form data: {list(request.form.keys())}")
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    lang = request.form.get('lang', 'en')

    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    try:
        # Extract text
        if AI_AVAILABLE:
            text = extract_text(file)
        else:
            text = demo_extract(file)

        # Store only first 800 chars to keep cookie small
        session['report_text'] = text[:800] if text else ''
        session['report_name'] = secure_filename(file.filename)

        # Get AI results
        if AI_AVAILABLE:
            explanation = explain_report(text, language=lang)
            risk = summarize_risk(text)
        else:
            explanation = demo_explain(text, lang)
            risk = demo_risk(text)

        # Save report to active family member
        from datetime import datetime as dt
        members = load_family()
        # Read from form data (not session - session cookie too large)
        active_idx_raw = request.form.get('active_member', '')
        active_idx = int(active_idx_raw) if active_idx_raw.strip().isdigit() else None
        if active_idx is not None and int(active_idx) < len(members):
            idx = int(active_idx)
            if 'reports' not in members[idx]:
                members[idx]['reports'] = []
            members[idx]['reports'].append({
                'name': secure_filename(file.filename),
                'date': dt.now().strftime('%d %b %Y'),
                'score': risk['score'],
                'level': risk['level'],
            })
            members[idx]['last_score'] = str(risk['score']) + '/100'
            members[idx]['last_scan'] = dt.now().strftime('%d %b %Y')
            save_family(members)

        # Update stats
        stats = session.get('stats', {'total': 0, 'last_score': '—', 'this_month': 0})
        stats['total'] += 1
        stats['last_score'] = f"{risk['score']}/100"
        stats['this_month'] += 1
        session['stats'] = stats

        # Update recent reports
        recent = session.get('recent_reports', [])
        from datetime import datetime
        recent.insert(0, {
            'name': secure_filename(file.filename),
            'date': datetime.now().strftime('%d %b %Y'),
            'score': risk['score'],
            'level': risk['level'],
            'color': risk['color'],
        })
        session['recent_reports'] = []  # cleared to keep cookie small

        # Save report to active family member
        from datetime import datetime
        members = load_family()
        active_idx = session.get('active_member', None)
        if active_idx is not None and active_idx < len(members):
            members[active_idx]['reports'].append({
                'name': secure_filename(file.filename),
                'date': datetime.now().strftime('%d %b %Y'),
                'score': risk['score'],
                'level': risk['level'],
                'explanation': explanation[:500],
            })
            members[active_idx]['last_score'] = f"{risk['score']}/100"
            members[active_idx]['last_scan'] = datetime.now().strftime('%d %b %Y')
            save_family(members)

        return jsonify({
            'ok': True,
            'explanation': explanation,
            'risk': risk,
            'report_name': secure_filename(file.filename),
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/chat')
def chat_page():
    report_name = session.get('report_name', '')
    return render_template('chat.html', report_name=report_name)

@app.route('/chat/send', methods=['POST'])
def chat_send():
    data = request.get_json()
    question = data.get('question', '')
    lang = data.get('lang', 'en')
    report_text = session.get('report_text', '')

    if not report_text:
        return jsonify({'error': 'No report uploaded'}), 400

    try:
        if AI_AVAILABLE:
            answer = chat_with_report(report_text, question, language=lang)
        else:
            answer = demo_chat(report_text, question, lang)
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/trends')
def trends():
    return render_template('trends.html')

@app.route('/trends/upload', methods=['POST'])
def trends_upload():
    files = request.files.getlist('files')
    lang = request.form.get('lang', 'en')
    results = []

    for i, f in enumerate(files):
        try:
            if AI_AVAILABLE:
                text = extract_text(f)
                values = extract_key_values(text)
            else:
                values = demo_keys(f)
            results.append({'label': f'Report {i+1}', 'name': f.filename, 'values': values})
        except Exception as e:
            results.append({'label': f'Report {i+1}', 'name': f.filename, 'values': {}, 'error': str(e)})

    return jsonify({'results': results})


import json, os

FAMILY_FILE = '/tmp/family_data.json'

def load_family():
    if os.path.exists(FAMILY_FILE):
        with open(FAMILY_FILE, 'r') as f:
            return json.load(f)
    return []

def save_family(members):
    with open(FAMILY_FILE, 'w') as f:
        json.dump(members, f)

@app.route('/family')
def family():
    members = load_family()
    return render_template('family.html', members=members)

@app.route('/family/data')
def family_data():
    members = load_family()
    return jsonify({'members': members})

@app.route('/family/add', methods=['POST'])
def family_add():
    data = request.get_json()
    members = load_family()
    members.append({
        'name': data.get('name'),
        'relation': data.get('relation'),
        'age': data.get('age'),
        'reports': []
    })
    save_family(members)
    return jsonify({'ok': True, 'members': members})

@app.route('/family/select/<int:idx>')
def family_select(idx):
    return jsonify({'ok': True})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
