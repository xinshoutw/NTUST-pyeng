"use client";
import {useEffect, useMemo, useState} from 'react';
import {motion} from 'framer-motion';
import {WordCard} from './WordCard';
import {
    COOKIE_EXPIRY,
    DEFAULT_PART,
    DEFAULT_TOPIC,
    fetchParts,
    fetchTopics,
    fetchWords,
    getCookie,
    parseParts,
    parseTopics,
    setCookie,
    topicLabelMapping,
    topicOrder,
} from '@/app/utils';
import {Word} from '@/app/types';
import Dropdown from './Dropdown';

interface Props {
    initialPart: string;
    initialTopic: string;
    initialWords: Word[];
    initialParts: number[];
    initialTopics: string[];
}


export default function WordsGrid(
    {
        initialPart,
        initialTopic,
        initialWords,
        initialParts,
        initialTopics
    }: Props) {
    const [lastSelectedPart, setLastSelectedPart] = useState<string>(initialPart);
    const [lastSelectedTopic, setLastSelectedTopic] = useState<string>(initialTopic);
    const [selectedPart, setSelectedPart] = useState<string>(initialPart);
    const [selectedTopic, setSelectedTopic] = useState<string>(initialTopic);
    const [words, setWords] = useState<Word[] | null>(initialWords);
    const [availableParts, setAvailableParts] = useState<number[]>(initialParts ?? []);
    const [availableTopics, setAvailableTopics] = useState<string[]>(initialTopics ?? []);
    const [loading, setLoading] = useState(!initialWords);
    const [openDropdown, setOpenDropdown] = useState<null | 'part' | 'topic'>(null);
    const [useGrid, setUseGrid] = useState(true);
    const [visibleCount, setVisibleCount] = useState<number>(0);

    useEffect(() => {
        const layout = getCookie('layout') || 'grid';
        setUseGrid(layout === 'grid');
    }, []);

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

    function onDropdownEvent(): void {
        // no cookie exist
        if (getCookie("lastPart") === null) {
            setCookie('lastPart', selectedPart);
        }
        if (getCookie("lastTopic") === null) {
            setCookie('lastTopic', selectedTopic);
        }

        // skip same page
        if (lastSelectedPart === selectedPart && lastSelectedTopic === selectedTopic) {
            return;
        }
        (async () => {
            setLoading(true);
            try {
                setWords((await fetchWords(selectedPart, selectedTopic)).words);

                if (selectedPart !== lastSelectedPart) {
                    setAvailableTopics(parseTopics(await fetchTopics(selectedPart)));
                    setLastSelectedPart(selectedPart);
                    setCookie('lastPart', selectedPart, COOKIE_EXPIRY);
                }

                if (selectedTopic !== lastSelectedTopic) {
                    const partData = await fetchParts(selectedTopic);
                    const newParts = parseParts(partData);
                    setAvailableParts(newParts);
                    setLastSelectedTopic(selectedTopic);
                    setCookie('lastTopic', selectedTopic, COOKIE_EXPIRY);
                }
            } catch (error) {
                console.error("Failed to load data:", error);

                setLastSelectedPart(DEFAULT_PART);
                setLastSelectedTopic(DEFAULT_TOPIC);
                setSelectedPart(DEFAULT_PART);
                setSelectedTopic(DEFAULT_TOPIC);

                const wordData = await fetchWords(DEFAULT_PART, DEFAULT_TOPIC);
                setWords(wordData.words);
                setAvailableTopics(parseTopics(await fetchTopics(DEFAULT_PART)));
                setCookie('lastPart', DEFAULT_PART, COOKIE_EXPIRY);
                setAvailableParts(parseParts(await fetchParts(DEFAULT_TOPIC)));
                setCookie('lastTopic', DEFAULT_TOPIC, COOKIE_EXPIRY);
            } finally {
                setLoading(false);
            }
        })();
    }

    /**
     * When select a dropdown, update word-cards and cookie.
     */
    useEffect(() => {
        onDropdownEvent()
    }, [selectedPart, selectedTopic, lastSelectedPart, lastSelectedTopic, initialPart, initialTopic]);

    const partOptions = useMemo(() => [
        {value: 'all', label: '全'}, ...availableParts
            .map(p => ({value: String(p), label: String(p)}))
    ], [availableParts]);

    const topicOptions = useMemo(() => [
        {value: 'all', label: '全'}, ...availableTopics
            .filter(t => t !== 'all')
            .map(t => ({value: t, label: t}))
    ], [availableTopics]);


    /**
     * Animated render cards
     */
    const cardDuration = 0.1;
    const desiredStaggerDelay = 0.05;
    const animatedWords = useMemo(() => {
        return words?.slice(0, Math.min(visibleCount, words.length)) || [];
    }, [words, visibleCount]);

    const immediateWords = useMemo(() => {
        return words?.slice(Math.min(visibleCount, words.length)) || [];
    }, [words, visibleCount]);

    const staggerChildren = animatedWords.length <= 1 ? 0 : desiredStaggerDelay;

    const containerVariants = {
        hidden: {},
        show: {transition: {staggerChildren}}
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
                    <br/>
                    由台科語言中心每週單字整理，配合劍橋辭典了解更多字義解釋與讀音
                </p>
                <div
                    className="flex flex-col md:flex-row md:flex-nowrap gap-4 justify-center items-center mt-6 relative z-10">
                    <Dropdown
                        label="Part"
                        options={partOptions}
                        selected={selectedPart}
                        onSelectAction={val => setSelectedPart(val)}
                        isOpen={openDropdown === 'part'}
                        onToggleAction={() => setOpenDropdown(openDropdown === 'part' ? null : 'part')}
                    />
                    <Dropdown
                        label="Topic"
                        options={topicOptions}
                        selected={selectedTopic}
                        onSelectAction={val => setSelectedTopic(val as string)}
                        isOpen={openDropdown === 'topic'}
                        onToggleAction={() => setOpenDropdown(openDropdown === 'topic' ? null : 'topic')}
                        sortOrder={topicOrder}
                        labelMapping={topicLabelMapping}
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
                                    className="flex flex-col h-full"
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
                                    className="break-inside-avoid flex flex-col h-full"
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
            {selectedTopic !== 'all' && selectedPart !== 'all' && (
                <a
                    href={`/practice?part=${selectedPart}&topic=${selectedTopic}`}
                    className="fixed bottom-4 right-4 py-3 px-4 bg-blue-600 text-white rounded shadow-lg hover:bg-blue-700 transition"
                >
                    Practice
                </a>
            )}
        </div>
    );
}
