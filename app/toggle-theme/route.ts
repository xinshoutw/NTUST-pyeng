import {NextResponse} from 'next/server';
import type {NextRequest} from 'next/server';

export const runtime = 'edge';

export async function GET(request: NextRequest) {
    const cookieStore = request.cookies;
    const currentTheme = cookieStore.get('theme')?.value;

    // 切換主題
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    // 取得請求的來源頁面
    const referer = request.headers.get('referer') || '/';

    // 設定新的 'theme' cookie
    const response = NextResponse.redirect(referer);
    response.cookies.set('theme', newTheme, {path: '/', maxAge: 60 * 60 * 24 * 365}); // 1 年

    return response;
}
