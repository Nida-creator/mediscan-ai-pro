
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
