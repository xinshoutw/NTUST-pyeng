import PracticeClient from '../../components/PracticeClient';
import { Suspense } from 'react'

export default function PracticePage() {
    return (
        <Suspense>
            <div className="max-w-md mx-auto p-4">
                <h1 className="text-2xl font-bold mb-4 text-center">
                    Practice
                </h1>
                <PracticeClient/>
            </div>
        </Suspense>
    );
}
