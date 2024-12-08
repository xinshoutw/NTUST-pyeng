import {PracticeEntry, Word} from './types';

export async function fetchWords(part?: number, topic?: string): Promise<{ words: Word[] }> {
    const url = 'https://py.xserver.tw/api/words';
    const params = new URLSearchParams();
    if (part) params.set('part', part.toString());
    if (topic) params.set('topic', topic);
    const res = await fetch(`${url}?${params.toString()}`, {cache: 'no-store'});
    if (!res.ok) throw new Error('Failed');
    return res.json();
}

export async function fetchParts(topic: string): Promise<{ count: number; parts: number[] }> {
    const res = await fetch(`https://py.xserver.tw/api/parts?topic=${topic}`, {cache: 'no-store'});
    if (!res.ok) throw new Error('Failed');
    return res.json();
}

export async function fetchTopics(part: number): Promise<{ count: number; topics: string[] }> {
    const res = await fetch(`https://py.xserver.tw/api/topics?part=${part}`, {cache: 'no-store'});
    if (!res.ok) throw new Error('Failed');
    return res.json();
}

export async function fetchPractice(part: number, topic: string): Promise<{ entries: PracticeEntry[] }> {
    const res = await fetch(`https://py.xserver.tw/api/practice/${part}/${topic}`, {cache: 'no-store'});
    if (!res.ok) throw new Error('Failed');
    return res.json();
}
