// /app/layout.tsx
import './globals.css';
import {ReactNode} from 'react';
import Footer from '../components/Footer';
import Link from 'next/link';
import {cookies} from 'next/headers'; // 正確導入 cookies

import ThemeToggleButton from '../components/ThemeToggleButton';

export const runtime = "edge";
export const metadata = {
    title: 'NTUST 英單學習網',
    description: '電爛你的同學，讓他知道你根本不用這個網站',
};

export default async function RootLayout({children}: { children: ReactNode }) {
    const cookieStore = await cookies();
    const themeCookie = cookieStore.get('theme')?.value || 'dark';
    const isDark = themeCookie === 'dark';

    return (
        <html lang="en" className={isDark ? 'dark' : ''}>
        <body
            className="bg-gray-50 text-gray-800 dark:bg-gray-900 dark:text-gray-100 min-h-screen flex flex-col transition-colors duration-300">
        <header className="bg-white dark:bg-gray-800 shadow fixed top-0 w-full z-50">
            <div className="max-w-5xl mx-auto p-4 flex items-center justify-between">
                <Link href="/" className="font-bold text-lg text-gray-800 dark:text-gray-100">
                    NTUST 英單學習網
                </Link>
                <nav className="space-x-4 flex items-center">
                    <Link href="/"
                          className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition">
                        Home
                    </Link>
                    <Link href="https://pygit.xserver.tw/"
                          className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition">
                        Repository
                    </Link>
                    {/* 主題切換按鈕 */}
                    <ThemeToggleButton/>
                </nav>
            </div>
        </header>
        <div className="pt-20 flex-1">
            {children}
        </div>
        <Footer/>
        </body>
        </html>
    );
}
