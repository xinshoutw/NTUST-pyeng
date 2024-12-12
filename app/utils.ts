import {PracticeEntry, Word} from './types';

export const API_ENDPOINT = "https://py.xserver.tw/api"
export const DEFAULT_PART = "1"
export const DEFAULT_TOPIC = "pvqc-ict"
// export const API_ENDPOINT = "http://0.0.0.0:8000/api"

export async function fetchWords(part?: number | null, topic?: string | null): Promise<{ words: Word[] }> {
    const params = new URLSearchParams();
    if (part) params.set('part', part.toString());
    if (topic) params.set('topic', topic);

    const res = await fetch(`${API_ENDPOINT}/words?${params.toString()}`, {next: {revalidate: 300}});
    if (!res.ok) throw new Error('Failed');
    return res.json();
}

export async function fetchParts(topic?: string | null): Promise<{ count: number; parts: number[] }> {
    const params = new URLSearchParams();
    if (topic) params.set('topic', topic);

    // console.log(`${API_ENDPOINT}/parts?${params.toString()}`)
    const res = await fetch(`${API_ENDPOINT}/parts?${params.toString()}`, {next: {revalidate: 300}});
    if (!res.ok) throw new Error('Failed');
    return res.json();
}

export async function fetchTopics(part?: number | null): Promise<{ count: number; topics: string[] }> {
    const params = new URLSearchParams();
    if (part) params.set('part', part.toString());

    // console.log(`${API_ENDPOINT}/topics?${params.toString()}`)
    const res = await fetch(`${API_ENDPOINT}/topics?${params.toString()}`, {next: {revalidate: 300}});
    if (!res.ok) throw new Error('Failed');
    return res.json();
}

export async function fetchPractice(part: number, topic: string): Promise<{ entries: PracticeEntry[] }> {
    const res = await fetch(`${API_ENDPOINT}/practice/${part}/${topic}`, {next: {revalidate: 300}});
    if (!res.ok) {
        throw new Error('Failed');
    }
    return res.json();
}


export function getCookie(name: string): string | null {
    const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? decodeURIComponent(match[2]) : null;
}

export function setCookie(name: string, value: string, days = 365) {
    const d = new Date();
    d.setTime(d.getTime() + days * 24 * 60 * 60 * 1000);
    const expires = "expires=" + d.toUTCString();
    document.cookie = `${name}=${encodeURIComponent(value)}; ${expires}; path=/`;
}

export function parsePart(str: string | number): number | null {
    return isNaN(Number(str)) ? null : Number(str);
}

export function parseTopic(str: string): string | null {
    return str === 'all' ? null : str;
}

export function parseParts(partData: { count: number, parts: number[] }): number[] {
    return [...(partData!.parts || [])].sort((a, b) => a - b)
}

export function parseTopics(topicData: { count: number, topics: string[] }): string[] {
    return ['all', ...topicData.topics.filter(t => t !== 'all')];
}

export const topicOrder = [
    'all',
    'toefl',
    'academic',
    'calculus',
    'ielts',
    'pvqc-ee',
    'pvqc-bm',
    'pvqc-me',
    'pvqc-dmd',
    'pvqc-ict',
];

export const topicLabelMapping: { [key: string]: string } = {
    'toefl': '托福',
    'academic': '學術',
    'calculus': '微積分',
    'ielts': '雅思',
    'pvqc-ee': '商業電子',
    'pvqc-bm': '商業管理',
    'pvqc-me': '機械工程',
    'pvqc-dmd': '多媒體',
    'pvqc-ict': '計算機',
};
