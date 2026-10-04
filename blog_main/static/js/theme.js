(() => {
    const toggle = document.getElementById('theme-toggle');
    if (!toggle) {
        return;
    }

    const icon = toggle.querySelector('i');
    const label = toggle.querySelector('span');
    const root = document.documentElement;

    const updateButton = () => {
        const isDark = root.dataset.theme === 'dark';
        toggle.setAttribute('aria-pressed', String(isDark));
        toggle.setAttribute('aria-label', `Switch to ${isDark ? 'light' : 'dark'} theme`);
        icon.className = `fa ${isDark ? 'fa-sun-o' : 'fa-moon-o'}`;
        label.textContent = isDark ? 'Light' : 'Dark';
    };

    updateButton();

    toggle.addEventListener('click', () => {
        const isDark = root.dataset.theme !== 'dark';
        if (isDark) {
            root.dataset.theme = 'dark';
        } else {
            delete root.dataset.theme;
        }

        try {
            localStorage.setItem('ink-insight-theme', isDark ? 'dark' : 'light');
        } catch (error) {
            // The current-page theme still works if browser storage is unavailable.
        }

        updateButton();
    });
})();
