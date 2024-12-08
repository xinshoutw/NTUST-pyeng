"use client";
import {memo, MouseEvent, useRef, useState} from 'react';
import {Word} from '@/app/types';

type WordCardProps = {
    wordData: Word;
};

function WordCardComponent({wordData}: WordCardProps) {
    const {word, pos, meaning, pronunciations, definitions, verbs} = wordData;
    const usPron = pronunciations?.find((p) => p.lang.toLowerCase() === 'us');
    const ukPron = pronunciations?.find((p) => p.lang.toLowerCase() === 'uk');
    const mainPos = usPron?.pos || ukPron?.pos || '';
    const hasPos = pos && pos !== '-';
    const posTags = hasPos ? pos.split('/') : [];
    const showIndicator = (definitions && definitions.length > 0) || (verbs && verbs.length > 0);

    const [expanded, setExpanded] = useState(false);
    const audioRef = useRef<HTMLAudioElement | null>(null);

    const playPronunciation = (e: MouseEvent<HTMLButtonElement>, url: string) => {
        e.stopPropagation();
        if (audioRef.current) {
            audioRef.current.src = url;
            audioRef.current.play();
        }
    };

    const hoverClass = 'transition transform hover:bg-gray-50 hover:shadow-lg hover:-translate-y-1 active:scale-95';

    return (
        <div
            className={`bg-white rounded-lg p-4 border-b border-gray-200 select-none relative 
      ${hoverClass} ${showIndicator ? 'cursor-pointer' : 'cursor-default'}`}
            onClick={() => showIndicator && setExpanded(!expanded)}
        >
            <div className="flex items-center justify-between mb-2">
                <h2 className="font-bold text-xl text-gray-900">{word}</h2>
                {hasPos && (
                    <div className="flex space-x-1">
                        {posTags.map((tag, i) => (
                            <span key={i} className="text-sm text-white bg-blue-500 px-2 py-1 rounded-full font-medium">
                {tag.trim()}
              </span>
                        ))}
                    </div>
                )}
            </div>
            <p className="text-gray-700 mb-4">{meaning}</p>
            {(usPron || ukPron) && (
                <div className="flex flex-wrap items-center space-x-2 mb-4">
                    {mainPos && <span className="text-xs text-gray-500 font-medium">{mainPos}:</span>}
                    {usPron && (
                        <button
                            type="button"
                            onClick={(e) => playPronunciation(e, usPron.url)}
                            className="text-xs text-blue-600 hover:underline flex items-center space-x-1"
                            style={{position: 'relative', top: '-3px'}}
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
                            className="text-xs text-blue-600 hover:underline flex items-center space-x-1"
                            style={{position: 'relative', top: '-3px'}}
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
                <div className="absolute bottom-2 right-2 text-blue-600">
                    <svg className={`w-4 h-4 transform transition ${expanded ? 'rotate-180' : 'rotate-0'}`}
                         fill="currentColor" viewBox="0 0 20 20">
                        <path
                            d="M5.23 7.21a.75.75 0 011.06-.02L10 10.74l3.7-3.55a.75.75 0 111.04 1.08l-4.25 4.07a.75.75 0 01-1.04 0L5.23 8.27a.75.75 0 01-.02-1.06z"/>
                    </svg>
                </div>
            )}
            {showIndicator && (
                <div
                    className={`transition-all duration-300 overflow-hidden ${expanded ? 'max-h-96 opacity-100 pt-2' : 'max-h-0 opacity-0'}`}>
                    <div className="space-y-2 text-sm text-gray-800">
                        {definitions && definitions.length > 0 && (
                            <div>
                                <h3 className="font-semibold text-gray-900">Definitions:</h3>
                                <ul className="list-disc list-inside">
                                    {definitions.map((d, idx) => (
                                        <li key={idx}>
                                            <span className="font-medium text-gray-900">{d.pos}</span>: {d.translation}
                                            {d.definition && ` (${d.definition})`}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}
                        {verbs && verbs.length > 0 && (
                            <div>
                                <h3 className="font-semibold text-gray-900">Verb Forms:</h3>
                                <ul className="list-disc list-inside">
                                    {verbs.map((v, idx) => (
                                        <li key={idx}>{v.type}: {v.text}</li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}

export const WordCard = memo(WordCardComponent);
export default WordCard;
