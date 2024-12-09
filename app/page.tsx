import {cookies} from 'next/headers';
import WordsGrid from '../components/WordsGrid';
import {fetchParts, fetchTopics, fetchWords} from './utils';
import {Word} from './types';

export default async function HomePage() {
    const cookieStore = await cookies();
    const savedPart = cookieStore.get('lastPart')?.value || '1';
    const savedTopic = cookieStore.get('lastTopic')?.value || 'pvqc-ict';

    let initialPart: number | null = null;
    let initialTopic: string | null = null;
    let initialWords: Word[] | null = null;
    let initialParts: number[] | null = null;
    let initialTopics: string[] | null = null;

    if (savedPart && savedTopic) {
        initialPart = isNaN(Number(savedPart)) ? null : Number(savedPart);
        initialTopic = savedTopic !== 'all' ? savedTopic : null;

        const wordData = await fetchWords(initialPart!, initialTopic || '');
        initialWords = wordData.words;

        const topicData = await fetchTopics(initialPart || 1);
        const partData = await fetchParts(initialTopic || 'pvqc-ict');

        initialTopics = ['all', ...topicData.topics.filter(t => t !== 'all')];
        initialParts = [...(partData.parts || [])].sort((a, b) => a - b);
    }

    return (
        <WordsGrid
            initialPart={initialPart}
            initialTopic={initialTopic}
            initialWords={initialWords}
            initialParts={initialParts}
            initialTopics={initialTopics}
        />
    );
}
