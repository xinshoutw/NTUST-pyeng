import {cookies} from 'next/headers';
import WordsGrid from '../components/WordsGrid';
import {
    DEFAULT_PART,
    DEFAULT_TOPIC,
    fetchParts,
    fetchTopics,
    fetchWords,
    parseParts,
    parseTopics,
} from './utils';

export const runtime = "edge";
export const metadata = {
    title: 'NTUST 英簡單',
    description: '由台科語言中心每週單字整理，配合劍橋辭典了解更多字義解釋與讀音',
};

export default async function HomePage() {
    const cookieStore = await cookies();
    const initialPart = cookieStore.get('lastPart')?.value || DEFAULT_PART;
    const initialTopic = cookieStore.get('lastTopic')?.value || DEFAULT_TOPIC;

    const wordData = await fetchWords(initialPart, initialTopic);
    const partData = await fetchParts(initialTopic);
    const topicData = await fetchTopics(initialPart);

    const initialParts = parseParts(partData);
    const initialTopics = parseTopics(topicData);

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
