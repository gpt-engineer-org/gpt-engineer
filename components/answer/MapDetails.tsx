// @ts-nocheck 
"use client";
import React, { useState } from 'react';
import { IconPlus, IconClose } from '@/components/ui/icons';

interface Place {
    cid: React.Key | null | undefined;
    latitude: number;
    longitude: number;
    title: string;
    address: string;
    rating: number;
    category: string;
    phoneNumber?: string;
    website?: string;
}

const LocationSidebar = ({ places }: { places: Place[] }) => {
    const [showMore, setShowMore] = useState(false);
    // only show the first 5 places
    places = places.slice(0, 4);

    return (
        <div className="bg-white dark:bg-gray-800 shadow-lg rounded-lg p-4 mt-4">
            <div className="flex items-center">
                <h2 className="text-lg font-semibold flex-grow text-black dark:text-white">Location Details</h2>
                {places.length > 3 && (
                    <div className="flex justify-center ml-2">
                        <button
                            className="text-black dark:text-white focus:outline-none"
                            onClick={() => setShowMore(!showMore)}>
                            {showMore ? <IconClose /> : <IconPlus />}
                        </button>
                    </div>
                )}
            </div>
            <div className={`space-y-4 transition-all duration-500 ${showMore ? 'max-h-[5000px]' : 'max-h-[300px]'} overflow-hidden`}>
                {places?.slice(0, showMore ? places.length : 3).map((place: Place) => (
                    <div key={place.cid} className="bg-gray-100 dark:bg-gray-700 rounded-lg p-4">
                        <h3 className="text-lg font-semibold mb-2">{place.title}</h3>
                        <p className="text-gray-600 dark:text-gray-400 text-sm mb-2">{place.address}</p>
                        <div className="flex items-center mb-2">
                            <span className="text-gray-600 dark:text-gray-400 text-sm mr-1">Rating:</span>
                            <div className="flex items-center">
                                {[...Array(5)].map((_, index) => (
                                    <svg
                                        key={index}
                                        className={`w-4 h-4 ${index < Math.floor(place.rating)
                                                ? 'text-yellow-400'
                                                : 'text-gray-300 dark:text-gray-500'
                                            }`}
                                        xmlns="http://www.w3.org/2000/svg"
                                        viewBox="0 0 20 20"
                                        fill="currentColor"
                                    >
                                        <path
                                            fillRule="evenodd"
                                            d="M10 15.585l-5.293 2.776.1-5.867L.416 8.222l5.875-.855L10 2.415l3.709 4.952 5.875.855-4.391 4.272.1 5.867L10 15.585z"
                                            clipRule="evenodd"
                                        />
                                    </svg>
                                ))}
                            </div>
                        </div>
                        <p className="text-gray-600 dark:text-gray-400 text-sm mb-2">Category: {place.category}</p>
                        {place.phoneNumber && (
                            <p className="text-gray-600 dark:text-gray-400 text-sm mb-2">
                                Phone: <a href={`tel:${place.phoneNumber}`} className="text-blue-500 hover:underline">{place.phoneNumber}</a>
                            </p>
                        )}
                        {place.website && (
                            <p className="text-gray-600 dark:text-gray-400 text-sm truncate">
                                Website: <a href={place.website} className="text-blue-500 hover:underline">{place.website}</a>
                            </p>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default LocationSidebar;