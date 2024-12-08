"use client";
import {useEffect, useState} from 'react';
import WordCard from './WordCard';
import {fetchParts, fetchTopics, fetchWords} from '@/app/utils';
import {Word} from '@/app/types';
import Dropdown from './Dropdown';

function getCookie(name: string) {
    const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? decodeURIComponent(match[2]) : null;
}

function setCookie(name: string, value: string, days = 365) {
    const d = new Date();
    d.setTime(d.getTime() + (days * 24 * 60 * 60 * 1000));
    const expires = "expires=" + d.toUTCString();
    document.cookie = name + "=" + encodeURIComponent(value) + "; " + expires + "; path=/";
}

type Props = {
    initialPart: number;
    initialTopic: string;
    initialWords: Word[];
    initialParts: number[];
    initialTopics: string[];
};

export default function WordsGrid({initialPart, initialTopic, initialWords, initialParts, initialTopics}: Props) {
    const [selectedPart, setSelectedPart] = useState<number | string>(initialPart);
    const [selectedTopic, setSelectedTopic] = useState<string>(initialTopic);
    const [words, setWords] = useState<Word[]>(initialWords);
    const [parts, setParts] = useState<number[]>(initialParts);
    const [topics, setTopics] = useState<string[]>(initialTopics);
    const [loading, setLoading] = useState(false);
    const [openDropdown, setOpenDropdown] = useState<null | 'part' | 'topic'>(null);
    const [useGrid, setUseGrid] = useState(true);

    useEffect(() => {
        const layout = getCookie('layout') || 'grid';
        setUseGrid(layout === 'grid');

        const savedPart = getCookie('lastPart');
        const savedTopic = getCookie('lastTopic');

        if (savedPart) {
            setSelectedPart(isNaN(Number(savedPart)) ? 'all' : Number(savedPart));
        }
        if (savedTopic) {
            setSelectedTopic(savedTopic);
        }
    }, []);

    const loadData = async (part: number | string, topic: string) => {
        setLoading(true);
        try {
            const partNum = (typeof part === 'string' && part === 'all') ? null : part;
            const topicStr = (topic === 'all') ? null : topic;
            const wordData = await fetchWords(partNum as number, topicStr || '');
            setWords(wordData.words);

            const tPart = partNum || 1;
            const tTopic = topicStr || 'academic';
            const topicData = await fetchTopics(tPart as number);
            const partData = await fetchParts(tTopic);

            const newTopicOptions = ['all', ...topicData.topics.filter(t => t !== 'all')];
            const newPartOptions = [...(partData.parts || [])].sort((a, b) => a - b);

            setTopics(newTopicOptions);
            setParts(newPartOptions);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        loadData(selectedPart, selectedTopic);
    }, [selectedPart, selectedTopic]);

    useEffect(() => {
        if (selectedPart) {
            setCookie('lastPart', String(selectedPart));
            setCookie('lastTopic', String(selectedTopic));
        }
    }, [selectedPart, selectedTopic]);

    const partOptions = [{value: 'all', label: 'All'}, ...parts.map(p => ({value: p, label: String(p)}))];
    const topicOptions = [{value: 'all', label: 'All'}, ...topics.filter(t => t !== 'all').map(t => ({
        value: t,
        label: t
    }))];

    // const toggleLayout = () => {
    //     const newVal = !useGrid;
    //     setUseGrid(newVal);
    //     setCookie('layout', newVal ? 'grid' : 'columns', 365);
    // };

    const currentPart = typeof selectedPart === 'string' && selectedPart === 'all' ? '' : selectedPart;

    return (
        <div className="max-w-5xl mx-auto relative px-4 sm:px-8 pb-10 overflow-visible">
            <div className="mb-10 space-y-4 text-center relative">
                {/*<button*/}
                {/*    onClick={toggleLayout}*/}
                {/*    className="absolute right-0 top-0 text-sm text-blue-600 hover:underline"*/}
                {/*>*/}
                {/*    {useGrid ? 'Switch to Columns' : 'Switch to Grid'}*/}
                {/*</button>*/}
                <p className="text-gray-600 max-w-xl mx-auto">
                    Do you see that involution guy?<br></br>
                    Yeah, it&#39;s you.
                </p>
                <div
                    className="flex flex-col md:flex-row md:flex-nowrap gap-4 justify-center items-center mt-6 relative z-10">
                    <Dropdown
                        label="Part"
                        options={partOptions}
                        selected={selectedPart}
                        onSelect={(val) => setSelectedPart(val)}
                        isOpen={openDropdown === 'part'}
                        onToggle={() => setOpenDropdown(openDropdown === 'part' ? null : 'part')}
                    />
                    <Dropdown
                        label="Topic"
                        options={topicOptions}
                        selected={selectedTopic}
                        onSelect={(val) => setSelectedTopic(val as string)}
                        isOpen={openDropdown === 'topic'}
                        onToggle={() => setOpenDropdown(openDropdown === 'topic' ? null : 'topic')}
                    />
                </div>
            </div>
            {loading && <div className="text-center text-gray-500">Loading...</div>}
            {!loading && (
                useGrid ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 items-start">
                        {words.map((w, index) => (
                            <WordCard key={w.word + index} wordData={w}/>
                        ))}
                    </div>
                ) : (
                    <div className="columns-1 md:columns-2 lg:columns-3 space-y-4" style={{columnGap: '1rem'}}>
                        {words.map((w, index) => (
                            <div key={w.word + index} className="break-inside-avoid">
                                <WordCard wordData={w}/>
                            </div>
                        ))}
                    </div>
                )
            )}

            <a
                href={`/practice?part=${currentPart || 1}&topic=${selectedTopic}`}
                className="fixed bottom-4 right-4 py-3 px-4 bg-blue-600 text-white rounded shadow-lg hover:bg-blue-700 transition"
            >
                Practice
            </a>
        </div>
    );
}
