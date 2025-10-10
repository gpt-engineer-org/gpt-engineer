import { useState, useEffect } from 'react';

function Spotify({ spotify }: { spotify: string }) {
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const timer = setTimeout(() => {
            setIsLoading(false);
        }, 400);

        return () => clearTimeout(timer);
    }, []);

    return (
        <div className="mt-4 overflow-hidden">
            {isLoading ? (
                <div className="animate-pulse flex space-x-4">
                    <div className="flex-1 space-y-4 py-1">
                        <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                        <div className="space-y-2">
                            <div className="h-4 bg-gray-200 rounded"></div>
                            <div className="h-4 bg-gray-200 rounded w-5/6"></div>
                        </div>
                    </div>
                </div>
            ) : (
                <iframe
                    src={`https://open.spotify.com/embed/track/${spotify}`}
                    width='100%'
                    height='80'
                    allow="encrypted-media"
                ></iframe>
            )}
        </div>
    );
}

export default Spotify;