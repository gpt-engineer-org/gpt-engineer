import { useState, useEffect } from 'react';
import { Card, CardContent } from "@/components/ui/card";
import {
    Carousel,
    CarouselContent,
    CarouselItem,
    CarouselNext,
    CarouselPrevious,
} from "@/components/ui/carousel";
import { YoutubeLogo } from '@phosphor-icons/react';

// 1. Define the 'Video' interface to represent a video object
interface Video {
    link: string;
}

// 2. Define the 'VideosComponentProps' interface to specify the props for the 'VideosComponent'
interface VideosComponentProps {
    videos: Video[];
}

// 3. Define the 'VideosComponent' functional component that accepts 'VideosComponentProps'
const VideosComponent: React.FC<VideosComponentProps> = ({ videos }) => {
    // 4. Declare state variables using the 'useState' hook
    const [loadedImages, setLoadedImages] = useState<boolean[]>([]);
    const [selectedVideo, setSelectedVideo] = useState<string | null>(null);

    // 5. Use the 'useEffect' hook to initialize the 'loadedImages' state based on the number of videos
    useEffect(() => {
        setLoadedImages(Array(videos.length).fill(false));
    }, [videos]);

    // 6. Define the 'handleImageLoad' function to update the 'loadedImages' state when an image is loaded
    const handleImageLoad = (index: number) => {
        setLoadedImages((prevLoadedImages) => {
            const updatedLoadedImages = [...prevLoadedImages];
            updatedLoadedImages[index] = true;
            return updatedLoadedImages;
        });
    };

    // 7. Define the 'handleVideoSelect' function to set the 'selectedVideo' state when a thumbnail is clicked
    const handleVideoSelect = (link: string) => {
        setSelectedVideo(link);
    };

    // 8. Define the 'VideosSkeleton' component to display a loading skeleton while videos are loading
    const VideosSkeleton = () => (
        <div className="w-full p-1 ">
            <div className="w-full overflow-hidden aspect-video mt-5">
                <div className="w-full h-full bg-gray-300 dark:bg-gray-700 rounded animate-pulse"></div>
            </div>
        </div>
    );

    // 9. Render the 'VideosComponent' JSX
    return (
        <div className="bg-white dark:bg-gray-800 shadow-lg rounded-lg mt-4 w-full px-2 flex items-center justify-center">
            {/* 10. Render the video carousel */}
            <Carousel
                opts={{
                    align: "start",
                }}
                orientation="vertical"
                className="w-full max-w-xs"
            >
                <CarouselContent className=" h-[175px] mx-auto">
                    {videos.length === 0 ? (
                        <VideosSkeleton />
                    ) : (
                        videos.map((video, index) => {
                            const videoId = getYouTubeVideoId(video.link);
                            const imageUrl = `https://i.ytimg.com/vi/${videoId}/hqdefault.jpg`;

                            return (
                                <CarouselItem key={index} className="py-5 md:basis-1/2 ">
                                    <div className="p-1">
                                        <Card>
                                            <CardContent className="flex items-center justify-center p-0  h-[150px]">
                                                {selectedVideo === video.link ? (
                                                    <iframe
                                                        src={`https://www.youtube.com/embed/${videoId}?autoplay=1`}
                                                        title={`YouTube Video ${index}`}
                                                        allowFullScreen
                                                        className="w-full h-full rounded-lg"
                                                        allow='autoplay'
                                                    ></iframe>
                                                ) : (
                                                    <div
                                                        className="rounded-lg w-full overflow-hidden aspect-video transition-all duration-200 cursor-pointer"
                                                        onClick={() => handleVideoSelect(video.link)}
                                                    >
                                                        <img
                                                            src={imageUrl}
                                                            alt={`Video ${index}`}
                                                            className={`clip-yt-img w-full h-auto rounded-lg transition-all duration-200 ${loadedImages[index] ? 'block' : 'hidden'}`}
                                                            onLoad={() => handleImageLoad(index)}
                                                        />
                                                    </div>
                                                )}
                                            </CardContent>
                                        </Card>
                                    </div>
                                </CarouselItem>
                            );
                        })
                    )}
                </CarouselContent>
                <div className="hidden lg:flex justify-center mt-2">
                    <CarouselPrevious className="top-[90px] left-[310px] " />
                    <CarouselNext className="bottom-[5px] left-[310px] w-8 h-8" />
                </div>
            </Carousel>
        </div>
    );
};

// 11. Define the 'getYouTubeVideoId' function to extract the YouTube video ID from a URL
const getYouTubeVideoId = (url: string) => {
    const match = url.match(/(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
    return match ? match[1] : '';
};

export default VideosComponent;