'use client';

import {useEffect, useState} from 'react';
import Cookies from 'js-cookie';

const THEME_COOKIE_KEY = 'theme';
const THEME_COOKIE_EXPIRY_DAYS = 365;
const DARK_CLASS = 'dark';

export default function ThemeToggleButton() {
    const [isDark, setIsDark] = useState(false);

    const applyTheme = (dark: boolean) => {
        if (dark) {
            document.documentElement.classList.add(DARK_CLASS);
            Cookies.set(THEME_COOKIE_KEY, 'dark', {expires: THEME_COOKIE_EXPIRY_DAYS});
        } else {
            document.documentElement.classList.remove(DARK_CLASS);
            Cookies.set(THEME_COOKIE_KEY, 'light', {expires: THEME_COOKIE_EXPIRY_DAYS});
        }
        setIsDark(dark);
    };

    useEffect(() => {
        const savedTheme = Cookies.get(THEME_COOKIE_KEY);
        if (savedTheme === 'dark') {
            applyTheme(true);
        } else if (savedTheme === 'light') {
            applyTheme(false);
        } else {
            // 若無 cookie，預設 dark 模式
            applyTheme(true);
        }
    }, []);

    const toggleTheme = () => {
        applyTheme(!isDark);
    };

    return (
        <button
            onClick={toggleTheme}
            className="ml-4 p-2 rounded bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 hover:bg-gray-300 dark:hover:bg-gray-600 transition"
        >
            Mode
        </button>
    );
}

