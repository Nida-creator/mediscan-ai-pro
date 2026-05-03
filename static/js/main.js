
const TRANSLATIONS = {
    en: {
        upload_title: 'Upload Your Medical Report',
        upload_subtitle: 'Supports: PDF, JPG, PNG - Lab Reports and Prescriptions',
        drag_drop: 'Drag and drop your report here',
        upload_btn: 'Choose File',
        analyzing: 'Analyzing your report with AI...',
        results_title: 'Your Results',
        risk_score: 'Health Risk Score',
    },
    ur: {
        upload_title: 'اپنی طبی رپورٹ اپ لوڈ کریں',
        upload_subtitle: 'سپورٹ کرتا ہے: PDF، JPG، PNG',
        drag_drop: 'اپنی رپورٹ یہاں گھسیٹیں',
        upload_btn: 'فائل منتخب کریں',
        analyzing: 'AI سے رپورٹ کا تجزیہ ہو رہا ہے...',
        results_title: 'آپ کے نتائج',
        risk_score: 'صحت کا خطرے کا اسکور',
    }
};

let currentLang = localStorage.getItem('lang') || 'en';

function toggleLang() {
    currentLang = currentLang === 'en' ? 'ur' : 'en';
    localStorage.setItem('lang', currentLang);
    document.getElementById('langLabel').textContent = currentLang === 'en' ? 'English' : 'Urdu';
    applyTranslations();
}

function applyTranslations() {
    const tr = TRANSLATIONS[currentLang] || TRANSLATIONS['en'];
    document.querySelectorAll('[data-key]').forEach(el => {
        const key = el.getAttribute('data-key');
        if (tr[key]) el.textContent = tr[key];
    });
    document.body.setAttribute('dir', currentLang === 'ur' ? 'rtl' : 'ltr');
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
    const saved = localStorage.getItem('lang') || 'en';
    currentLang = saved;
    document.getElementById('langLabel').textContent = saved === 'en' ? 'English' : 'Urdu';
    applyTranslations();
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
