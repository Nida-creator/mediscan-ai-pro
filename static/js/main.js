// MediScan AI Pro — Main JS

// ── Language System ───────────────────────────────────────────────────────────
const TRANSLATIONS = {
    en: {
        upload_title: 'Upload Your Medical Report',
        upload_subtitle: 'Supports: PDF, JPG, PNG — Lab Reports & Prescriptions',
        drag_drop: 'Drag & drop your report here',
        upload_btn: 'Choose File',
        analyzing: 'Analyzing your report with AI...',
        results_title: 'Your Results',
        risk_score: 'Health Risk Score',
    },
    ur: {
        upload_title: 'اپنی طبی رپورٹ اپ لوڈ کریں',
        upload_subtitle: 'سپورٹ کرتا ہے: PDF، JPG، PNG — لیب رپورٹس',
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
    document.getElementById('langLabel').textContent = currentLang === 'en' ? '🇬🇧 English' : '🇵🇰 اردو';
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

// ── Name / User System ────────────────────────────────────────────────────────
function showNameModal() {
    document.getElementById('nameModal').classList.add('show');
    setTimeout(() => document.getElementById('nameInput').focus(), 100);
}

function saveName() {
    const name = document.getElementById('nameInput').value.trim();
    if (!name) return;
    document.getElementById('userName').textContent = name;
    document.getElementById('nameModal').classList.remove('show');

    // Update welcome name if on dashboard
    const welcomeName = document.getElementById('welcomeName');
    if (welcomeName) welcomeName.textContent = name;

    // Save to server session
    fetch('/set-name', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
    });
}

// Allow Enter key in name input
document.addEventListener('DOMContentLoaded', () => {
    const nameInput = document.getElementById('nameInput');
    if (nameInput) {
        nameInput.addEventListener('keydown', e => {
            if (e.key === 'Enter') saveName();
        });
    }

    // Apply saved language
    const saved = localStorage.getItem('lang') || 'en';
    currentLang = saved;
    document.getElementById('langLabel').textContent = saved === 'en' ? '🇬🇧 English' : '🇵🇰 اردو';
    applyTranslations();

    // Show name modal if first visit
    const savedName = localStorage.getItem('userName');
    if (savedName) {
        document.getElementById('userName').textContent = savedName;
        const welcomeName = document.getElementById('welcomeName');
        if (welcomeName) welcomeName.textContent = savedName;
    } else {
        setTimeout(showNameModal, 600);
    }
});

// ── Sidebar Toggle ────────────────────────────────────────────────────────────
function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
}

// Close modal on overlay click
document.addEventListener('click', e => {
    const modal = document.getElementById('nameModal');
    if (e.target === modal) modal.classList.remove('show');
});
