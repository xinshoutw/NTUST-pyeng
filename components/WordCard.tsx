"use client";
import {AnimatePresence, motion} from 'framer-motion';
import {memo, MouseEvent, useRef, useState} from 'react';
import {Word} from '@/app/types';

type WordCardProps = {
    wordData: Word;
};

const EXPAND_ANIMATION_DURATION = 0.25;

function WordCardComponent({wordData}: WordCardProps) {
    const {word, pos, meaning, pronunciations, definitions, verbs} = wordData;
    const usPron = pronunciations?.find((p) => p.lang.toLowerCase() === 'us');
    const ukPron = pronunciations?.find((p) => p.lang.toLowerCase() === 'uk');
    const primaryPos = usPron?.pos || ukPron?.pos || '';
    const hasPos = pos && pos !== '-';
    const posTags = hasPos ? pos.split('/') : [];
    const showIndicator = (definitions && definitions.length > 0) || (verbs && verbs.length > 0);

    const [expanded, setExpanded] = useState(false);
    const [playbackError, setPlaybackError] = useState<string | null>(null); // 新增錯誤狀態
    const audioRef = useRef<HTMLAudioElement | null>(null);

    /**
     * 按下播音按紐
     */
    const playPronunciation = async (e: MouseEvent<HTMLButtonElement>, url: string) => {
        e.stopPropagation();
        setPlaybackError(null);
        if (audioRef.current) {
            try {
                audioRef.current.src = url;
                await audioRef.current.play();
            } catch (error) {
                console.error("Failed to play pronunciation:", error);
                setPlaybackError("播放發音時出錯，請稍後再試。");
            }
        }
    };

    return (
        <div
            className={`relative flex flex-col bg-white dark:bg-gray-800 rounded-lg p-4 border-b border-gray-200 dark:border-gray-700 select-none transition transform hover:bg-gray-50 hover:shadow-lg hover:-translate-y-1 active:scale-95 ${
                showIndicator ? 'cursor-pointer' : 'cursor-default'
            }`}
            onClick={() => showIndicator && setExpanded((prev) => !prev)}
        >
            <div className="flex items-center justify-between mb-2">
                <h2 className="font-bold text-xl text-gray-900 dark:text-gray-100">{word}</h2>
                {hasPos && (
                    <div className="flex space-x-1">
                        {posTags.map((tag, i) => (
                            <span key={i}
                                  className="text-sm text-white bg-blue-500 dark:bg-blue-600 px-2 py-1 rounded-full font-medium">
                                {tag.trim()}
                            </span>
                        ))}
                    </div>
                )}
            </div>
            <p className="text-gray-700 dark:text-gray-200 mb-4 flex-grow">{meaning}</p>
            {(usPron || ukPron) && (
                <div className="flex flex-wrap items-center space-x-2 mb-4">
                    {primaryPos && (
                        <span className="text-xs text-gray-500 dark:text-gray-400 font-medium">{primaryPos}:</span>
                    )}
                    {usPron && (
                        <button
                            type="button"
                            onClick={(e) => playPronunciation(e, usPron.url)}
                            className="text-xs text-blue-600 dark:text-blue-400 hover:underline flex items-center space-x-1 relative"
                            style={{top: '-3px'}}
                        >
                            <svg className="w-4 h-4 relative" style={{top: '1px'}} fill="currentColor">
                                <path d="M3 9v6h4l5 5V4L7 9H3z"></path>
                            </svg>
                            <span>US</span>
                        </button>
                    )}
                    {ukPron && (
                        <button
                            type="button"
                            onClick={(e) => playPronunciation(e, ukPron.url)}
                            className="text-xs text-blue-600 dark:text-blue-400 hover:underline flex items-center space-x-1 relative"
                            style={{top: '-3px'}}
                        >
                            <svg className="w-4 h-4 relative" style={{top: '1px'}} fill="currentColor">
                                <path d="M3 9v6h4l5 5V4L7 9H3z"></path>
                            </svg>
                            <span>UK</span>
                        </button>
                    )}
                    <audio ref={audioRef}/>
                </div>
            )}
            {showIndicator && (
                <div className="absolute bottom-2 right-2 text-blue-600 dark:text-blue-400">
                    <svg className={`w-4 h-4 transform transition ${expanded ? 'rotate-180' : 'rotate-0'}`}
                         fill="currentColor" viewBox="0 0 20 20">
                        <path
                            d="M5.23 7.21a.75.75 0 011.06-.02L10 10.74l3.7-3.55a.75.75 0 111.04 1.08l-4.25 4.07a.75.75 0 01-1.04 0L5.23 8.27a.75.75 0 01-.02-1.06z"/>
                    </svg>
                </div>
            )}
            {showIndicator && (
                <AnimatePresence>
                    {expanded && (
                        <motion.div
                            initial={{maxHeight: 0, opacity: 0, paddingTop: 0}}
                            animate={{maxHeight: 1000, opacity: 1, paddingTop: '.3rem'}}
                            exit={{maxHeight: 0, opacity: 0, paddingTop: 0}}
                            transition={{duration: EXPAND_ANIMATION_DURATION}}
                            className="overflow-hidden"
                        >
                            <div className="space-y-2 text-sm text-gray-800 dark:text-gray-200">
                                {definitions && definitions.length > 0 && (
                                    <div>
                                        <h3 className="font-semibold text-gray-900 dark:text-gray-100">Definitions:</h3>
                                        <ul className="list-disc list-inside">
                                            {definitions.map((d, idx) => (
                                                <li key={idx}>
                                                    <span
                                                        className="font-medium text-gray-900 dark:text-gray-100">{d.pos}</span>: {d.translation}
                                                    {d.definition && ` (${d.definition})`}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                                {verbs && verbs.length > 0 && (
                                    <div>
                                        <h3 className="font-semibold text-gray-900 dark:text-gray-100">Verb Forms:</h3>
                                        <ul className="list-disc list-inside">
                                            {verbs.map((v, idx) => (
                                                <li key={idx}>{v.type}: {v.text}</li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            )}
            {playbackError && (
                <div className="mt-2 text-red-500 dark:text-red-400 text-sm">
                    {playbackError}
                </div>
            )}
        </div>
    );
}

export const WordCard = memo(WordCardComponent);
