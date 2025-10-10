"use client";
import React, { useRef } from 'react';
import 'leaflet/dist/leaflet.css';
import dynamic from 'next/dynamic';

import L from 'leaflet';
const MapContainer = dynamic(() => import('react-leaflet').then((mod) => mod.MapContainer), { ssr: false });
const TileLayer = dynamic(() => import('react-leaflet').then((mod) => mod.TileLayer), { ssr: false });
const Marker = dynamic(() => import('react-leaflet').then((mod) => mod.Marker), { ssr: false });
const Popup = dynamic(() => import('react-leaflet').then((mod) => mod.Popup), { ssr: false });

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

const Map = ({ places }: { places: Place[] }) => {
    const customIcon = L.icon({
        iconUrl: 'https://cdn.jsdelivr.net/npm/leaflet@1.7.1/dist/images/marker-icon.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
    });
    const mapRef = useRef<L.Map | null>(null);

    const center = places.length > 0
        ? [
            places.reduce((acc, place) => acc + place.latitude / places.length, 0),
            places.reduce((acc, place) => acc + place.longitude / places.length, 0)
        ]
        : [0, 0];

    return (
        <div className={`bg-white dark:bg-gray-800 shadow-lg rounded-lg p-4 mt-4 `}>
            <div className="flex items-center">
                <h2 className="text-lg font-semibold flex-grow text-black dark:text-white">Locations</h2>
            </div>
            <div className={`mt-4`}>
                <MapContainer
                    // @ts-ignore
                    center={center}
                    zoom={13}
                    style={{ height: '400px' }}
                    attributionControl={false}
                    className="rounded-lg overflow-hidden"
                    zoomControl={false}
                    ref={mapRef}
                >
                    <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                    {places.map((place: Place) => (
                        <Marker
                            key={place.cid}
                            position={[place.latitude, place.longitude]}
                            icon={customIcon}
                        >
                            <Popup>
                                <div className="bg-white rounded-lg">
                                    <h3 className="text-lg font-semibold mb-1">{place.title}</h3>
                                    <p className="text-gray-600 text-sm mb-1">{place.address}</p>
                                    <div className="flex items-center mb-1">
                                        <span className="text-gray-600 text-sm mr-1">Rating:</span>
                                        <div className="flex items-center">
                                            {[...Array(5)].map((_, index) => (
                                                <svg
                                                    key={index}
                                                    className={`w-4 h-4 ${index < Math.floor(place.rating) ? 'text-yellow-400' : 'text-gray-300'
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
                                    <p className="text-gray-600 text-sm mb-1">Category: {place.category}</p>
                                    {place.phoneNumber && <p className="text-gray-600 text-sm mb-1">Phone: {place.phoneNumber}</p>}
                                    {place.website && (
                                        <p className="text-gray-600 text-sm">
                                            Website: <a href={place.website} className="text-blue-500 hover:underline">{place.website}</a>
                                        </p>
                                    )}
                                </div>
                            </Popup>
                        </Marker>
                    ))}
                </MapContainer>
            </div>
        </div>
    );
};

const DynamicMap = dynamic(() => Promise.resolve(Map), { ssr: false });

export default DynamicMap;