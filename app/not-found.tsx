import {HTTPAccessErrorFallback} from './error-fallback'

export const runtime = 'edge';

export default function NotFound() {
    return (
        <HTTPAccessErrorFallback
            status={404}
            message="This page could not be found."
        />
    )
}