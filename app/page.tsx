import {cookies} from 'next/headers';
import WordsGrid from '../components/WordsGrid';
import {
    fetchParts, fetchTopics, fetchWords,
    parsePart, parseTopic,
    parseParts, parseTopics
} from './utils';

export default async function HomePage() {
    const cookieStore = await cookies();

    let savedPart = cookieStore.get('lastPart')?.value;
    if (savedPart === undefined) {
        savedPart = '1'
        cookieStore.set('lastPart', savedPart)
    }

    let savedTopic = cookieStore.get('lastTopic')?.value;
    if (savedTopic === undefined) {
        savedTopic = 'pvqc-ict'
        cookieStore.set('lastTopic', savedTopic)
    }

    const initialPart: number | null = parsePart(savedPart);
    const initialTopic: string | null = parseTopic(savedTopic);
    const wordData = await fetchWords(initialPart, initialTopic);
    const partData = await fetchParts(initialTopic);
    const topicData = await fetchTopics(initialPart);
    const initialParts: number[] = parseParts(partData);
    const initialTopics: string[] = parseTopics(topicData);

    return (
        <WordsGrid
            initialPart={initialPart}
            initialTopic={initialTopic}
            initialWords={wordData.words}
            initialParts={initialParts}
            initialTopics={initialTopics}
        />
    );
}
