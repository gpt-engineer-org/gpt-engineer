import { useState, useEffect } from 'react';
import { Card, CardContent } from "@/components/ui/card";
import {
    Carousel,
    CarouselContent,
    CarouselItem,
    CarouselNext,
    CarouselPrevious,
} from "@/components/ui/carousel";
import Autoplay from 'embla-carousel-autoplay';
import {
    Dialog,
    DialogClose,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface Image {
    link: string;
    alt?: string;
}

interface ImagesComponentProps {
    images: Image[];
}

const ImagesComponent: React.FC<ImagesComponentProps> = ({ images }) => {
    const [loadedImages, setLoadedImages] = useState<boolean[]>([]);
    const [isOpen, setIsOpen] = useState(false);
    const [photoIndex, setPhotoIndex] = useState(0);

    useEffect(() => {
        setLoadedImages(Array(images.length).fill(false));
    }, [images]);

    const handleImageLoad = (index: number) => {
        setLoadedImages((prevLoadedImages) => {
            const updatedLoadedImages = [...prevLoadedImages];
            updatedLoadedImages[index] = true;
            return updatedLoadedImages;
        });
    };

    const ImagesSkeleton = () => (
        <div className="w-full p-1 ">
            <div className="w-full overflow-hidden aspect-video mt-5">
                <div className="w-full h-full bg-gray-300 dark:bg-gray-700 rounded animate-pulse"></div>
            </div>
        </div>
    );

    const currentImage = images[photoIndex];

    return (
        <div className="bg-white dark:bg-gray-800 shadow-lg rounded-lg mt-4 w-full px-2 flex items-center justify-center">
            <Carousel
                plugins={[
                    Autoplay({
                        delay: 2000,
                    }),
                ]}
                opts={{
                    align: "start",
                }}
                orientation="vertical"
                className="w-full max-w-xs"
            >
                <CarouselContent className="h-[175px]">
                    {images.length === 0 ? (
                        <ImagesSkeleton />
                    ) : (
                        images.map((image, index) => (
                            <CarouselItem key={image.link} className="py-5 md:basis-1/2">
                                <div className="p-1">
                                    <Card>
                                        <CardContent className="flex items-center justify-center p-0 h-[150px]">
                                            <div
                                                className="relative w-full h-full cursor-pointer"
                                                onClick={() => {
                                                    setPhotoIndex(index);
                                                    setIsOpen(true);
                                                }}
                                            >
                                                {!loadedImages[index] && (
                                                    <div className="absolute inset-0 flex items-center justify-center bg-gray-200">
                                                        <span className="text-gray-500">Loading...</span>
                                                    </div>
                                                )}
                                                <img
                                                    src={image.link}
                                                    alt={image.alt || 'Image'}
                                                    className={`w-full h-full object-cover rounded-lg ${loadedImages[index] ? 'block' : 'hidden'}`}
                                                    onLoad={() => handleImageLoad(index)}
                                                />
                                            </div>
                                        </CardContent>
                                    </Card>
                                </div>
                            </CarouselItem>
                        ))
                    )}
                </CarouselContent>
                <div className="hidden lg:flex justify-center mt-2 ">
                    <CarouselPrevious className="top-[90px] left-[310px]" />
                    <CarouselNext className="bottom-[5px] left-[310px] w-8 h-8" />
                </div>
            </Carousel>
            <Dialog open={isOpen} onOpenChange={setIsOpen}>
                <DialogContent className="md:max-w-screen-md bg-opacity-80 z-[999999999999]">
                    {currentImage && (
                        <>
                            <Carousel
                                plugins={[
                                    Autoplay({
                                        delay: 2000,
                                    }),
                                ]}
                                opts={{
                                    align: "start",
                                }}
                                orientation="horizontal"
                                className="w-full"
                            >
                                <CarouselContent className="h-[500px]">
                                    {images.map((image, index) => (
                                        <CarouselItem key={image.link} className="py-5">
                                            <div className="flex items-center justify-center max-w-[700px] max-h-[500px] overflow-hidden">
                                                <img
                                                    src={image.link}
                                                    alt={image.alt || 'Image'}
                                                    className="w-full h-auto object-cover rounded-lg"
                                                />
                                            </div>
                                        </CarouselItem>
                                    ))}
                                </CarouselContent>
                                <div className="flex justify-space-between mt-2">
                                    {/* <CarouselPrevious className="mr-8" />
                                    <CarouselNext className="ml-8" /> */}
                                </div>
                            </Carousel>
                        </>
                    )}
                </DialogContent>
            </Dialog>
        </div>
    );
};

export default ImagesComponent;