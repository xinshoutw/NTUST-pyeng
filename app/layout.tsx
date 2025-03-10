import './globals.css';
import {ReactNode} from 'react';
import Footer from '../components/Footer';
import Link from 'next/link';
import {cookies} from 'next/headers';
import Image from 'next/image';
import ThemeToggleButton from '../components/ThemeToggleButton';

export const runtime = "edge";
export const metadata = {
    title: 'NTUST 英簡單',
    description: '由台科語言中心每週單字整理，配合劍橋辭典了解更多字義解釋與讀音',
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
                    {/* unfixable issue, use <a> instead of <Link> */}
                    {/* ref: https://github.com/vercel/next.js/discussions/57565 */}
                    <a href="/"
                       className="flex items-center font-bold text-lg text-gray-800 dark:text-gray-100 hover:text-gray-600 dark:hover:text-gray-300 transition-colors">
                        <Image
                            src="/android-chrome-192x192.png"
                            alt="Icon"
                            width={32}
                            height={32}
                            className="mr-2 rounded-full shadow-sm"
                            priority={true}
                        />
                        NTUST 英簡單
                    </a>
                    <nav className="space-x-4 flex items-center">
                        <Link href="https://r.xinshou.tw/ntust-eng-git"
                              className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition">
                            Repository
                        </Link>
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
