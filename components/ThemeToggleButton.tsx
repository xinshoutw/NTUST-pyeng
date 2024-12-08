'use client';

import {useEffect, useState} from 'react';
import Cookies from 'js-cookie';

export default function ThemeToggleButton() {
    const [isDark, setIsDark] = useState(false);

    useEffect(() => {
        const theme = Cookies.get('theme');
        if (theme === 'dark') {
            setIsDark(true);
            document.documentElement.classList.add('dark');
        } else if (theme === 'light') {
            setIsDark(false);
            document.documentElement.classList.remove('dark');
        } else {
            Cookies.set('theme', 'dark', {expires: 365});
            setIsDark(true);
            document.documentElement.classList.add('dark');
        }
    }, []);


    const toggleTheme = () => {
        if (isDark) {
            document.documentElement.classList.remove('dark');
            Cookies.set('theme', 'light', {expires: 365});
            setIsDark(false);
        } else {
            document.documentElement.classList.add('dark');
            Cookies.set('theme', 'dark', {expires: 365});
            setIsDark(true);
        }
    };

    return (
        <button
            onClick={toggleTheme}
            className="ml-4 p-2 rounded bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 hover:bg-gray-300 dark:hover:bg-gray-600 transition"
        >
            {isDark ? 'Light Mode' : 'Dark Mode'}
        </button>
    );
}
