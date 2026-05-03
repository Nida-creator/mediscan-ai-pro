// fix name saving
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
    const savedName = localStorage.getItem('userName');
    if (savedName) {
        document.getElementById('userName').textContent = savedName;
        const welcomeName = document.getElementById('welcomeName');
        if (welcomeName) welcomeName.textContent = savedName;
    } else {
        setTimeout(showNameModal, 600);
    }

    const nameInput = document.getElementById('nameInput');
    if (nameInput) {
        nameInput.addEventListener('keydown', e => {
            if (e.key === 'Enter') saveName();
        });
    }

    const saved = localStorage.getItem('lang') || 'en';
    currentLang = saved;
    document.getElementById('langLabel').textContent = saved === 'en' ? '🇬🇧 English' : '🇵🇰 اردو';
    applyTranslations();
});
