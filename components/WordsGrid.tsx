"use client";
import {useEffect, useState, useMemo} from 'react';
import {motion} from 'framer-motion';
import {WordCard} from './WordCard';
import {fetchParts, fetchTopics, fetchWords} from '@/app/utils';
import {Word} from '@/app/types';
import Dropdown from './Dropdown';

type Props = {
    initialPart: number | null;
    initialTopic: string | null;
    initialWords: Word[] | null;
    initialParts: number[] | null;
    initialTopics: string[] | null;
};

function getCookie(name: string): string | null {
    const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? decodeURIComponent(match[2]) : null;
}

function setCookie(name: string, value: string, days = 365) {
    const d = new Date();
    d.setTime(d.getTime() + days * 24 * 60 * 60 * 1000);
    const expires = "expires=" + d.toUTCString();
    document.cookie = `${name}=${encodeURIComponent(value)}; ${expires}; path=/`;
}

export default function WordsGrid({
                                      initialPart,
                                      initialTopic,
                                      initialWords,
                                      initialParts,
                                      initialTopics
                                  }: Props) {
    const [selectedPart, setSelectedPart] = useState<number | string>(initialPart ?? 'all');
    const [selectedTopic, setSelectedTopic] = useState<string>(initialTopic ?? 'all');
    const [words, setWords] = useState<Word[] | null>(initialWords);
    const [parts, setParts] = useState<number[]>(initialParts ?? []);
    const [topics, setTopics] = useState<string[]>(initialTopics ?? []);
    const [loading, setLoading] = useState(!initialWords);
    const [openDropdown, setOpenDropdown] = useState<null | 'part' | 'topic'>(null);
    const [useGrid, setUseGrid] = useState(true);
    const [visibleCount, setVisibleCount] = useState<number>(0);

    useEffect(() => {
        const updateVisibleCount = () => {
            const width = window.innerWidth;
            if (width >= 1024) { // lg
                setVisibleCount(30);
            } else if (width >= 768) { // md
                setVisibleCount(20);
            } else { // sm
                setVisibleCount(10);
            }
        };

        updateVisibleCount();
        window.addEventListener('resize', updateVisibleCount);
        return () => window.removeEventListener('resize', updateVisibleCount);
    }, []);

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
            const tTopic = topicStr || 'pvqc-ict';
            const topicData = await fetchTopics(tPart as number);
            const partData = await fetchParts(tTopic);

            const newTopicOptions = ['all', ...topicData.topics.filter(t => t !== 'all')];
            const newPartOptions = [...(partData.parts || [])].sort((a, b) => a - b);

            setTopics(newTopicOptions);
            setParts(newPartOptions);
        } catch (error) {
            console.error("Failed to load data:", error);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        if (initialWords && selectedPart === initialPart && selectedTopic === initialTopic) {
            return;
        }
        loadData(selectedPart!, selectedTopic!);
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

    const animatedWords = useMemo(() => {
        return words?.slice(0, Math.min(visibleCount, words.length)) || [];
    }, [words, visibleCount]);

    const immediateWords = useMemo(() => {
        return words?.slice(Math.min(visibleCount, words.length)) || [];
    }, [words, visibleCount]);

    const cardDuration = 0.1;
    const desiredStaggerDelay = 0.05;

    const staggerChildren = useMemo(() => {
        if (animatedWords.length <= 1) return 0;
        return desiredStaggerDelay;
    }, [animatedWords.length, desiredStaggerDelay]);

    const containerVariants = {
        hidden: {},
        show: {
            transition: {
                staggerChildren,
            }
        }
    };

    const itemVariants = {
        hidden: {opacity: 0, y: 10},
        show: {
            opacity: 1,
            y: 0,
            transition: {duration: cardDuration, ease: 'easeOut'}
        }
    };

    return (
        <div className="max-w-5xl mx-auto relative px-4 sm:px-8 pb-10 overflow-visible">
            <div className="mb-10 space-y-4 text-center relative">
                {/*<button
                    onClick={toggleLayout}
                    className="absolute right-0 top-0 text-sm text-blue-600 hover:underline"
                >
                    {useGrid ? 'Switch to Columns' : 'Switch to Grid'}
                </button>*/}
                <p className="max-w-xl mx-auto">
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
            {!loading && words && (
                <>
                    {useGrid ? (
                        <motion.div
                            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 items-stretch"
                            variants={containerVariants}
                            initial="hidden"
                            animate="show"
                            style={{gridAutoRows: 'auto'}}
                        >
                            {animatedWords.map((w, index) => (
                                <motion.div
                                    variants={itemVariants}
                                    key={w.word + index}
                                    className="flex flex-col h-full" // 確保字卡填滿容器
                                >
                                    <WordCard wordData={w}/>
                                </motion.div>
                            ))}
                        </motion.div>
                    ) : (
                        <motion.div
                            className="columns-1 md:columns-2 lg:grid-cols-3 space-y-4"
                            style={{columnGap: '1rem'}}
                            variants={containerVariants}
                            initial="hidden"
                            animate="show"
                        >
                            {animatedWords.map((w, index) => (
                                <motion.div
                                    variants={itemVariants}
                                    key={w.word + index}
                                    className="break-inside-avoid flex flex-col h-full" // 確保字卡填滿容器
                                >
                                    <WordCard wordData={w}/>
                                </motion.div>
                            ))}
                        </motion.div>
                    )}

                    {immediateWords.length > 0 && (
                        useGrid ? (
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-4 items-stretch">
                                {immediateWords.map((w, index) => (
                                    <div
                                        key={w.word + (visibleCount + index)}
                                        className="flex flex-col h-full"
                                    >
                                        <WordCard wordData={w}/>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="columns-1 md:columns-2 lg:grid-cols-3 space-y-4 mt-4"
                                 style={{columnGap: '1rem'}}>
                                {immediateWords.map((w, index) => (
                                    <div
                                        key={w.word + (visibleCount + index)}
                                        className="break-inside-avoid flex flex-col h-full"
                                    >
                                        <WordCard wordData={w}/>
                                    </div>
                                ))}
                            </div>
                        )
                    )}
                </>
            )}
            {selectedTopic !== 'all' && selectedPart !== 'all' &&
                <a
                    href={`/practice?part=${currentPart || 1}&topic=${selectedTopic}`}
                    className="fixed bottom-4 right-4 py-3 px-4 bg-blue-600 text-white rounded shadow-lg hover:bg-blue-700 transition"
                >
                    Practice
                </a>
            }
        </div>
    );
}
