import {PracticeEntry, Word} from './types';

export const API_ENDPOINT = "https://pyeng-backend.xserver.tw/api";
export const DEFAULT_PART = "1";
export const DEFAULT_TOPIC = "pvqc-ict";
export const COOKIE_EXPIRY = 365;

async function fetchJson(url: string) {
    const res = await fetch(url, {next: {revalidate: 300}});
    if (!res.ok) {
        throw new Error(`Fetch error: ${url}`);
    }
    return res.json();
}

export async function fetchWords(part: string, topic: string): Promise<{ words: Word[] }> {
    const topic_f = parseTopic(topic);
    const part_f = parsePart(part);

    const params = new URLSearchParams();
    if (part_f) params.set('part', part_f);
    if (topic_f) params.set('topic', topic_f);

    return fetchJson(`${API_ENDPOINT}/words?${params.toString()}`);
}

export async function fetchParts(topic: string): Promise<{ count: number; parts: number[] }> {
    const topic_f = parseTopic(topic);
    const params = new URLSearchParams();
    if (topic_f) params.set('topic', topic_f);

    return fetchJson(`${API_ENDPOINT}/parts?${params.toString()}`);
}

export async function fetchTopics(part: string): Promise<{ count: number; topics: string[] }> {
    const part_f = parsePart(part);
    const params = new URLSearchParams();
    if (part_f) params.set('part', part_f);

    return fetchJson(`${API_ENDPOINT}/topics?${params.toString()}`);
}

export async function fetchPractice(part: string, topic: string): Promise<{ entries: PracticeEntry[] }> {
    return fetchJson(`${API_ENDPOINT}/practice/${part}/${topic}`);
}

export function getCookie(name: string): string | null {
    const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? decodeURIComponent(match[2]) : null;
}

export function setCookie(name: string, value: string, days = COOKIE_EXPIRY) {
    const d = new Date();
    d.setTime(d.getTime() + days * 24 * 60 * 60 * 1000);
    const expires = "expires=" + d.toUTCString();
    document.cookie = `${name}=${encodeURIComponent(value)}; ${expires}; path=/`;
}

function parsePart(str: string): string | null {
    return isNaN(Number(str)) ? null : str;
}

function parseTopic(str: string): string | null {
    return str === 'all' ? null : str;
}

export function parseParts(partData: { count: number; parts: number[] }): number[] {
    return [...(partData!.parts || [])].sort((a, b) => a - b);
}

export function parseTopics(topicData: { count: number; topics: string[] }): string[] {
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
