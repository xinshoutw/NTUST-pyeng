import {cookies} from 'next/headers';
import WordsGrid from '../components/WordsGrid';
import {
    DEFAULT_PART, DEFAULT_TOPIC,
    fetchParts, fetchTopics, fetchWords,
    parseParts, parseTopics,
} from './utils';

export default async function HomePage() {
    const cookieStore = await cookies();

    const part = cookieStore.get('lastPart')?.value ?? DEFAULT_PART;
    const topic = cookieStore.get('lastTopic')?.value ?? DEFAULT_TOPIC;
    const wordData = await fetchWords(part, topic);
    const partData = await fetchParts(topic);
    const topicData = await fetchTopics(part);
    const initialParts: number[] = parseParts(partData);
    const initialTopics: string[] = parseTopics(topicData);

    return (
        <WordsGrid
            initialPart={part}
            initialTopic={topic}
            initialWords={wordData.words}
            initialParts={initialParts}
            initialTopics={initialTopics}
        />
    );
}
