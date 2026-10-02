/**
 * WSaPS Theme Manager
 * Supports: 'light', 'dark', and 'system' modes.
 * Displays 3-icon selector UI (Sun, Moon, Desktop).
 */
(function() {
    function getStoredMode() {
        return localStorage.getItem('wsaps-theme') || 'system';
    }

    function getSystemPreference() {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    function resolveTheme(mode) {
        if (mode === 'system') {
            return getSystemPreference();
        }
        return mode === 'light' ? 'light' : 'dark';
    }

    function applyTheme(mode) {
        const theme = resolveTheme(mode);
        document.documentElement.setAttribute('data-theme', theme);
        if (theme === 'dark') {
            document.documentElement.classList.add('dark');
            document.documentElement.classList.remove('light');
        } else {
            document.documentElement.classList.remove('dark');
            document.documentElement.classList.add('light');
        }
        
        // Update active class on all 3-icon selector buttons
        document.querySelectorAll('[data-theme-set]').forEach(btn => {
            const btnMode = btn.getAttribute('data-theme-set');
            if (btnMode === mode) {
                btn.classList.add('bg-brand-blue', 'text-white', 'shadow-sm', 'font-semibold');
                btn.classList.remove('text-gray-400', 'hover:text-white', 'opacity-60');
                btn.setAttribute('aria-pressed', 'true');
            } else {
                btn.classList.remove('bg-brand-blue', 'text-white', 'shadow-sm', 'font-semibold');
                btn.classList.add('text-gray-400', 'hover:text-white', 'opacity-60');
                btn.setAttribute('aria-pressed', 'false');
            }
        });
    }

    function setMode(mode) {
        localStorage.setItem('wsaps-theme', mode);
        applyTheme(mode);
    }

    // Apply immediately to prevent FOUC
    const currentMode = getStoredMode();
    applyTheme(currentMode);

    // Listen for OS theme changes when in 'system' mode
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleSystemChange = () => {
        if (getStoredMode() === 'system') {
            applyTheme('system');
        }
    };
    if (mediaQuery.addEventListener) {
        mediaQuery.addEventListener('change', handleSystemChange);
    } else if (mediaQuery.addListener) {
        mediaQuery.addListener(handleSystemChange);
    }

    // Bind event handlers on DOM content loaded
    document.addEventListener('DOMContentLoaded', function() {
        const activeMode = getStoredMode();
        applyTheme(activeMode);

        document.querySelectorAll('[data-theme-set]').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                const selectedMode = this.getAttribute('data-theme-set');
                setMode(selectedMode);
            });
        });
    });

    window.setWsapsTheme = setMode;
})();
