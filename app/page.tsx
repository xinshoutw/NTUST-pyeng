import {cookies} from 'next/headers';
import WordsGrid from '../components/WordsGrid';
import {
    DEFAULT_PART,
    DEFAULT_TOPIC,
    fetchHeartbeat,
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
    let initialPart = cookieStore.get('lastPart')?.value || DEFAULT_PART;
    let initialTopic = cookieStore.get('lastTopic')?.value || DEFAULT_TOPIC;

    // 檢查後端心跳
    const heartbeatStatus = await fetchHeartbeat();
    if (heartbeatStatus === 502) {
        return (
            <div className="flex justify-center items-center h-screen text-2xl text-pink-500">
                後端服務尚未啟動，請稍後再試
            </div>
        );
    } else if (heartbeatStatus !== 200) {
        // 處理其他非預期的狀態碼或錯誤
        return (
            <div className="flex justify-center items-center h-screen text-2xl text-red-500">
                無法連接到後端服務，請稍後再試
            </div>
        );
    }

    let wordData, partData, topicData;
    try {
        // 第一次嘗試用 cookie 中的 part / topic 來抓資料
        wordData = await fetchWords(initialPart, initialTopic);
        partData = await fetchParts(initialTopic);
        topicData = await fetchTopics(initialPart);
    } catch (error) {
        console.error('資料抓取失敗，使用預設值:', error);
        initialPart = DEFAULT_PART;
        initialTopic = DEFAULT_TOPIC;

        wordData = await fetchWords(initialPart, initialTopic);
        partData = await fetchParts(initialTopic);
        topicData = await fetchTopics(initialPart);
    }

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
