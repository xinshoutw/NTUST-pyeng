"use client";

import {useEffect, useState} from 'react';
import {PracticeEntry} from '@/app/types';
import {fetchPractice} from '@/app/utils';
import {useSearchParams} from 'next/navigation';

export default function PracticeClient() {
    const searchParams = useSearchParams();
    const urlPart = searchParams.get('part');
    const urlTopic = searchParams.get('topic');

    const part = urlPart ? Number(urlPart) : null;
    const topic = urlTopic || null;

    const [entries, setEntries] = useState<PracticeEntry[] | null>(null);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [selectedChoice, setSelectedChoice] = useState<number | null>(null);
    const [feedback, setFeedback] = useState<string | null>(null);
    const [errors, setErrors] = useState(0);
    const [attempted, setAttempted] = useState(false);
    const [showResults, setShowResults] = useState(false);

    useEffect(() => {
        if (!part || !topic) return;

        let mounted = true;
        (async () => {
            try {
                const data = await fetchPractice(part, topic);
                if (mounted) setEntries(data.entries);
            } catch {
                setEntries([]);
                return <div className="p-4 text-center text-gray-500">No practice data...</div>;
            }
        })();
        return () => {
            mounted = false;
        };
    }, [part, topic]);

    if (!part || !topic) return <div className="p-4 text-center text-gray-500">No part/topic specified.</div>;
    if (!entries) return <div className="p-4 text-center text-gray-500">Loading...</div>;
    const total = entries.length;
    if (total === 0) return <div className="p-4 text-center text-gray-500">No practice data...</div>;

    const currentEntry = entries[currentIndex];
    const correctAnswer = currentEntry.answer;
    const correctCount = total - errors;
    const accuracy = total > 0 ? ((correctCount / total) * 100).toFixed(1) : 0;
    const choices = currentEntry.choices;
    const correctIndex = choices.findIndex(c => c.choice_text === correctAnswer);

    const handleChoice = (idx: number) => {
        if (attempted) return;
        setAttempted(true);
        setSelectedChoice(idx);

        const choiceText = choices[idx].choice_text;
        if (choiceText === correctAnswer) {
            // setFeedback("Correct!");
        } else {
            // setFeedback(`Wrong! The correct answer is "${correctAnswer}".`);
            setErrors(e => e + 1);
        }
    };

    const handleNext = () => {
        if (currentIndex < total - 1) {
            setCurrentIndex(currentIndex + 1);
            setSelectedChoice(null);
            setFeedback(null);
            setAttempted(false);
        }
    };

    const handleShowResult = () => {
        setShowResults(true);
    };

    if (showResults) {
        return (
            <div
                className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow relative select-none text-center transition-colors duration-300">
                <h3 className="font-bold text-2xl mb-4 text-gray-900 dark:text-gray-100">Practice Complete!</h3>
                <p className="text-md text-gray-700 dark:text-gray-300 mb-6">Accuracy: {accuracy}%</p>
                {errors > 0 ? (
                    <p className="text-md text-red-500 dark:text-red-400">Review the incorrect answers for
                        improvement.</p>
                ) : (
                    <p className="text-md text-green-500 dark:text-green-400">Perfect score! 🎉</p>
                )}
                <div className="mt-6">
                    <a
                        href={`/practice/?part=${part}&topic=${topic}`}
                        className="inline-block px-6 py-3 bg-blue-600 dark:bg-blue-500 text-white rounded-lg shadow-md hover:bg-blue-700 dark:hover:bg-blue-600 transition-colors duration-300 transform hover:scale-105"
                    >
                        Start New Practice
                    </a>
                </div>
            </div>
        );
    }

    const highlightCorrect = (i: number) =>
        (attempted && selectedChoice !== correctIndex && i === correctIndex) ?
            'bg-green-300 dark:bg-green-700 hover:bg-green-400 hover:dark:bg-green-600' : '';

    return (
        <div
            className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow relative select-none transition-colors duration-300">
            <div className="mb-6 flex flex-col items-center space-y-2">
                <h3 className="font-bold text-2xl text-gray-800 dark:text-gray-100">Part: {part}, Topic: {topic}</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">Errors: {errors} / {total}</p>
            </div>

            {(
                <>
                    <h3 className="font-semibold text-lg text-gray-800 dark:text-gray-100 mb-2">{currentEntry.question}</h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">Question {currentIndex + 1} of {total}</p>
                    <div className="space-y-2">
                        {choices.map((c, i) => {
                            const isSelected = selectedChoice === i;
                            const isCorrect = c.choice_text === correctAnswer;

                            return (
                                <button
                                    key={c.choice_order}
                                    type="button"
                                    onClick={() => handleChoice(i)}
                                    disabled={attempted}
                                    className={`w-full text-left py-2 px-4 border rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition relative
                        // ${isSelected && isCorrect ? 'border-green-500 bg-green-300 dark:bg-green-700 hover:bg-green-400 hover:dark:bg-green-600' : ''}
                        ${isSelected && !isCorrect ? 'border-red-500 bg-red-300 dark:bg-red-700 hover:bg-red-400 hover:dark:bg-red-600' : ''}
                        ${attempted ? 'opacity-60 cursor-not-allowed' : ''}
                        ${highlightCorrect(i)}`}
                                >
                                    {c.choice_text}
                                    {isSelected && (
                                        <span className={`absolute right-4 top-1/2 transform -translate-y-1/2 text-sm font-bold
                                      ${isCorrect ? 'text-green-500 dark:text-green-400' : 'text-red-500 dark:text-red-400'} transition-all`}>
                                      {isCorrect ? '✓' : '✗'}
                                    </span>
                                    )}
                                </button>
                            );
                        })}
                    </div>
                    {feedback &&
                        <div className="mt-4 text-center text-sm text-gray-600 dark:text-gray-400">{feedback}</div>}
                    <div className="mt-6 text-center">
                        {currentIndex < total - 1 ? (
                            <button
                                type="button"
                                onClick={handleNext}
                                disabled={!attempted}
                                className="bg-blue-600 dark:bg-blue-500 text-white py-2 px-6 rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 transition disabled:bg-gray-300 dark:disabled:bg-gray-600 disabled:cursor-not-allowed"
                            >
                                Next Question
                            </button>
                        ) : (
                            attempted && (
                                <button
                                    type="button"
                                    onClick={handleShowResult}
                                    className="bg-blue-600 dark:bg-blue-500 text-white py-2 px-6 rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 transition"
                                >
                                    Show Result
                                </button>
                            )
                        )}
                    </div>
                </>
            )}
        </div>
    );
}
