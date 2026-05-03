
const TRANSLATIONS = {

    en: {
        upload_title: 'Upload Your Medical Report',
        upload_subtitle: 'Supports: PDF, JPG, PNG - Lab Reports and Prescriptions',
        drag_drop: 'Drag and drop your report here',
        upload_btn: 'Choose File',
        analyzing: 'Analyzing your report with AI...',
        results_title: 'Your Results',
        risk_score: 'Health Risk Score',
        tagline: 'Smart Scans. Accurate Insights. Better Care.',
        chat_placeholder: 'Ask about your report...',
        chat_title: 'AI Doctor Chat',
        chat_sub: 'Ask anything about your uploaded lab report',
        chat_suggested: 'Suggested Questions',
        q1: 'Should I be worried about my results?',
        q2: 'What does my hemoglobin level mean?',
        q3: 'Is my glucose level normal?',
        q4: 'What lifestyle changes should I make?',
        q5: 'Do I need to see a doctor urgently?',
        dash_welcome_sub: 'AI-driven insights to help you understand your health.',
        dash_total_reports: 'Total Reports',
        dash_last_score: 'Last Risk Score',
        dash_this_month: 'Reports This Month',
        dash_accuracy: 'AI Accuracy',
        dash_risk_title: 'AI Risk Assessment',
        dash_new_scan: 'New Scan Analysis',
        dash_recent: 'Recent Reports',
        dash_upload_report: 'Upload Report',
        dash_ask_ai: 'Ask AI Doctor',
        dash_trends: 'Health Trends',
        dash_family: 'Family Profiles',
        dash_drag: 'Drag & drop reports here',
        trends_title: 'Health Trends',
        trends_sub: 'Track your health over time across multiple scans',
        trends_upload_title: 'Upload Reports (Oldest → Newest)',
        trends_select: 'Select 2 or more lab reports',
        family_title: 'Family Profiles',
        family_sub: 'Manage health records for your entire family',
    },
    ur: {
        upload_title: 'اپنی طبی رپورٹ اپ لوڈ کریں',
        upload_subtitle: 'سپورٹ کرتا ہے: PDF، JPG، PNG',
        drag_drop: 'اپنی رپورٹ یہاں گھسیٹیں',
        upload_btn: 'فائل منتخب کریں',
        analyzing: 'AI سے رپورٹ کا تجزیہ ہو رہا ہے...',
        results_title: 'آپ کے نتائج',
        risk_score: 'صحت کا خطرے کا اسکور',
        tagline: 'سمارٹ اسکین۔ درست معلومات۔ بہتر صحت۔',
        chat_placeholder: 'رپورٹ کے بارے میں پوچھیں...',
        chat_title: 'AI ڈاکٹر چیٹ',
        chat_sub: 'اپنی لیب رپورٹ کے بارے میں کچھ بھی پوچھیں',
        chat_suggested: 'تجویز کردہ سوالات',
        q1: 'کیا مجھے اپنے نتائج کی فکر کرنی چاہیے؟',
        q2: 'میرے ہیموگلوبن کی سطح کا کیا مطلب ہے؟',
        q3: 'کیا میری گلوکوز کی سطح نارمل ہے؟',
        q4: 'مجھے کیا طرز زندگی میں تبدیلیاں کرنی چاہئیں؟',
        q5: 'کیا مجھے فوری ڈاکٹر سے ملنے کی ضرورت ہے؟',
        dash_welcome_sub: 'AI سے چلنے والی معلومات جو آپ کی صحت سمجھنے میں مدد کرے۔',
        dash_total_reports: 'کل رپورٹس',
        dash_last_score: 'آخری خطرے کا اسکور',
        dash_this_month: 'اس ماہ کی رپورٹس',
        dash_accuracy: 'AI درستگی',
        dash_risk_title: 'AI خطرے کا جائزہ',
        dash_new_scan: 'نئی اسکین تجزیہ',
        dash_recent: 'حالیہ رپورٹس',
        dash_upload_report: 'رپورٹ اپلوڈ کریں',
        dash_ask_ai: 'AI ڈاکٹر سے پوچھیں',
        dash_trends: 'صحت کے رجحانات',
        dash_family: 'خاندانی پروفائل',
        dash_drag: 'رپورٹس یہاں گھسیٹیں',
        trends_title: 'صحت کے رجحانات',
        trends_sub: 'متعدد اسکینز میں وقت کے ساتھ اپنی صحت کو ٹریک کریں',
        trends_upload_title: 'رپورٹس اپلوڈ کریں (پرانی سے نئی)',
        trends_select: '2 یا زیادہ لیب رپورٹس منتخب کریں',
        family_title: 'خاندانی پروفائل',
        family_sub: 'پورے خاندان کے صحت کے ریکارڈ منظم کریں',
    }

};

let currentLang = localStorage.getItem('lang') || 'en';

function toggleLang() {
    currentLang = currentLang === 'en' ? 'ur' : 'en';
    localStorage.setItem('lang', currentLang);
    applyLang();
}

function applyLang() {
    const tr = TRANSLATIONS[currentLang];
    const isUrdu = currentLang === 'ur';

    document.body.setAttribute('dir', isUrdu ? 'rtl' : 'ltr');

    const langLabel = document.getElementById('langLabel');
    if (langLabel) langLabel.textContent = isUrdu ? '🇵🇰 اردو' : '🇬🇧 English';

    const tagline = document.querySelector('.topbar-tagline');
    if (tagline) tagline.textContent = tr.tagline;

    document.querySelectorAll('[data-key]').forEach(el => {
        const key = el.getAttribute('data-key');
        if (tr[key]) el.textContent = tr[key];
    });

    const chatInput = document.getElementById('chatInput');
    if (chatInput) chatInput.placeholder = tr.chat_placeholder;

    const navLabels = {
        '/': isUrdu ? 'ڈیش بورڈ' : 'Dashboard',
        '/scan': isUrdu ? 'رپورٹ اسکین' : 'Scan Report',
        '/chat': isUrdu ? 'AI ڈاکٹر چیٹ' : 'AI Doctor Chat',
        '/trends': isUrdu ? 'صحت کے رجحانات' : 'Health Trends',
        '/family': isUrdu ? 'خاندانی پروفائل' : 'Family Profiles',
    };
    document.querySelectorAll('.nav-item span').forEach(el => {
        const href = el.closest('a')?.getAttribute('href');
        if (href && navLabels[href]) el.textContent = navLabels[href];
    });
}

function showNameModal() {
    document.getElementById('nameModal').classList.add('show');
    setTimeout(() => document.getElementById('nameInput').focus(), 100);
}

function saveName() {
    const name = document.getElementById('nameInput').value.trim();
    if (!name) return;
    localStorage.setItem('userName', name);
    document.getElementById('userName').textContent = name;
    document.getElementById('nameModal').classList.remove('show');
    const welcomeName = document.getElementById('welcomeName');
    if (welcomeName) welcomeName.textContent = name;
    fetch('/set-name', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const nameInput = document.getElementById('nameInput');
    if (nameInput) {
        nameInput.addEventListener('keydown', e => {
            if (e.key === 'Enter') saveName();
        });
    }

    currentLang = localStorage.getItem('lang') || 'en';
    applyLang();

    const savedName = localStorage.getItem('userName');
    if (savedName) {
        document.getElementById('userName').textContent = savedName;
        const welcomeName = document.getElementById('welcomeName');
        if (welcomeName) welcomeName.textContent = savedName;
    } else {
        setTimeout(showNameModal, 600);
    }
});

function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
}

document.addEventListener('click', e => {
    const modal = document.getElementById('nameModal');
    if (e.target === modal) modal.classList.remove('show');
});
