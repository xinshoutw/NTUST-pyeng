import './globals.css'
import {ReactNode} from 'react'
import Footer from '../components/Footer'
import Link from 'next/link'

export const metadata = {
    title: 'NTUST 英單學習網',
    description: '電爛你的同學，讓他知道你根本不用這個網站',
}

export default function RootLayout({children}: { children: ReactNode }) {
    return (
        <html lang="en">
        <body className="bg-gray-50 text-gray-800 min-h-screen flex flex-col">
        <header className="bg-white shadow fixed top-0 w-full z-50">
            <div className="max-w-5xl mx-auto p-4 flex items-center justify-between">
                <Link href="/" className="font-bold text-lg">NTUST 英單學習網 </Link>
                <nav className="space-x-4">
                    <Link href="/" className="text-gray-600 hover:text-gray-900 transition">Home</Link>
                    <Link href="https://pygit.xserver.tw/"
                          className="text-gray-600 hover:text-gray-900 transition">Repository</Link>
                </nav>
            </div>
        </header>
        <div className="pt-20 flex-1">
            {children}
        </div>
        <Footer/>
        </body>
        </html>
    )
}
