import {cookies} from 'next/headers';
import WordsGrid from '../components/WordsGrid';
import {
    DEFAULT_PART, DEFAULT_TOPIC,
    fetchParts, fetchTopics, fetchWords,
    parsePart, parseTopic,
    parseParts, parseTopics,
} from './utils';

export default async function HomePage() {
    const cookieStore = await cookies();

    const savedPart = cookieStore.get('lastPart')?.value ?? DEFAULT_PART;
    const savedTopic = cookieStore.get('lastTopic')?.value ?? DEFAULT_TOPIC;
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
