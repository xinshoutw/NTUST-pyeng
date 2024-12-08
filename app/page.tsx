import {fetchParts, fetchTopics, fetchWords} from './utils';
import WordsGrid from '../components/WordsGrid';
import {Word} from './types';

export default async function HomePage() {
    const initialPart = 1;
    const initialTopic = 'pvqc-ict';
    const wordData = await fetchWords(initialPart, initialTopic);
    const topicData = await fetchTopics(initialPart);
    const partData = await fetchParts(initialTopic);
    return (
        <WordsGrid
            initialPart={initialPart}
            initialTopic={initialTopic}
            initialWords={wordData.words as Word[]}
            initialParts={partData.parts}
            initialTopics={topicData.topics}
        />
    );
}
