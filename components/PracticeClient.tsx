"use client";

import {useEffect, useState} from 'react';
import {PracticeEntry} from '@/app/types';
import {fetchPractice} from '@/app/utils';
import {useSearchParams} from 'next/navigation';

export default function PracticeClient() {
    const searchParams = useSearchParams();
    const urlPart = searchParams.get('part');
    const urlTopic = searchParams.get('topic');

    const part = urlPart ? Number(urlPart) : 2;
    const topic = urlTopic || 'academic';

    const [entries, setEntries] = useState<PracticeEntry[] | null>(null);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [selectedChoice, setSelectedChoice] = useState<number | null>(null);
    const [feedback, setFeedback] = useState<string | null>(null);
    const [errors, setErrors] = useState(0);
    const [attempted, setAttempted] = useState(false);

    useEffect(() => {
        let mounted = true;
        (async () => {
            const data = await fetchPractice(part, topic);
            if (mounted) setEntries(data.entries);
        })();
        return () => {
            mounted = false;
        };
    }, [part, topic]);

    if (!entries) return <div className="p-4 text-center text-gray-500">Loading...</div>;
    const total = entries.length;
    if (total === 0) return <div className="p-4 text-center text-gray-500">No practice data...</div>;

    const currentEntry = entries[currentIndex];
    const correctAnswer = currentEntry.answer;
    const done = (currentIndex === total - 1 && feedback !== null);
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
            setFeedback("Correct!");
        } else {
            setFeedback(`Wrong! The correct answer is "${correctAnswer}".`);
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

    return (
        <div className="bg-white p-4 rounded shadow relative select-none">
            <div className="mb-4 flex flex-col items-center space-y-2">
                <h3 className="font-bold text-xl">Part: {part}, Topic: {topic}</h3>
                <p className="text-sm text-gray-500">Errors: {errors} / {total}</p>
            </div>

            {!done && (
                <>
                    <h3 className="font-bold mb-2">{currentEntry.question}</h3>
                    <p className="text-sm text-gray-500 mb-4">Question {currentIndex + 1} of {total}</p>
                    <div className="space-y-2">
                        {choices.map((c, i) => {
                            const isSelected = selectedChoice === i;
                            const isCorrect = c.choice_text === correctAnswer;

                            const highlightCorrect = (attempted && selectedChoice !== correctIndex && i === correctIndex)
                                ? 'bg-green-100'
                                : '';

                            return (
                                <button
                                    key={c.choice_order}
                                    type="button"
                                    onClick={() => handleChoice(i)}
                                    disabled={attempted}
                                    className={`w-full text-left py-2 px-4 border rounded hover:bg-gray-100 transition relative 
                                        ${isSelected && isCorrect ? 'border-green-500' : ''} 
                                        ${isSelected && !isCorrect ? 'border-red-500' : ''} 
                                        ${attempted ? 'opacity-60 cursor-not-allowed' : ''} 
                                        ${highlightCorrect}`}
                                >
                                    {c.choice_text}
                                    {isSelected && (
                                        <span className={`absolute right-2 top-1/2 transform -translate-y-1/2 text-sm font-bold 
                                            ${isCorrect ? 'text-green-500' : 'text-red-500'} transition-all`}>
                                            {isCorrect ? '✓' : '✗'}
                                        </span>
                                    )}
                                </button>
                            );
                        })}
                    </div>
                    {feedback && <div className="mt-4 text-center text-sm">{feedback}</div>}
                    <div className="mt-4 text-center">
                        {currentIndex < total - 1 ? (
                            <button
                                type="button"
                                onClick={handleNext}
                                disabled={!attempted}
                                className="bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 transition disabled:bg-gray-300 disabled:cursor-not-allowed"
                            >
                                Next Question
                            </button>
                        ) : (
                            feedback && (
                                <div className="text-green-600 font-bold mt-4">
                                    All done! Great job.
                                </div>
                            )
                        )}
                    </div>
                </>
            )}

            {done && (
                <div className="text-center">
                    <h3 className="font-bold text-xl mb-2">Practice Complete!</h3>
                    <p className="text-sm text-gray-600 mb-4">Accuracy: {accuracy}%</p>
                    {errors > 0 ? (
                        <p className="text-sm text-gray-600">Review the incorrect answers for improvement.</p>
                    ) : (
                        <p className="text-sm text-gray-600">Perfect score! No errors. :3</p>
                    )}
                </div>
            )}
        </div>
    );
}
