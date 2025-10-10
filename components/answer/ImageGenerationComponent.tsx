// 1. Define the 'ImageProps' interface with optional 'src' and 'query' properties
interface ImageProps {
    src?: string;
    query?: string;
}

// 2. Define the 'Image' functional component that takes 'src' and 'query' as props
export default function Image({ src, query }: ImageProps) {
    // 3. Render the 'Image' component
    return (
        <div className="flex flex-col max-w-[1200px] mx-auto">
            <div className="flex items-center max-w-[1200px] max-h-full shadow-lg p-4 mt-4 rounded-lg relative">
                {!src ? (
                    // 4. Render the skeleton loader only for the image
                    <div className="w-[600px] h-[600px] bg-gray-300 rounded-lg animate-pulse mr-6"></div>
                ) : (
                    <img
                        src={src}
                        alt="Full size"
                        className="w-[600px] h-[600px] rounded-lg mr-6"
                    />
                )}
                <div className="flex-1 flex flex-col justify-center items-center">
                    {query && (
                        <div className="text-black text-xl font-bold mb-4">
                            {query}
                        </div>
                    )}
                </div>
                <div className="absolute bottom-4 right-4">
                    <img
                        src="./fal.svg"
                        alt="powered by fal.ai"
                        className="h-6"
                    />
                </div>
            </div>
        </div>
    );
}