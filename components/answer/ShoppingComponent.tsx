// 1. Import the 'useState' hook from React
import { useState } from 'react';
import { IconPlus, IconClose } from '@/components/ui/icons';

// 2. Define the 'ShoppingItem' interface based on the structure of the shopping data
interface ShoppingItem {
    title: string;
    source: string;
    link: string;
    price: string;
    delivery: string;
    imageUrl: string;
    rating: number;
    ratingCount: number;
    offers: string;
    productId: string;
    position: number;
}

// 3. Define the 'ShoppingComponentProps' interface with a 'shopping' property of type 'ShoppingItem[]'
interface ShoppingComponentProps {
    shopping: ShoppingItem[];
}

// 4. Define the 'ShoppingComponent' functional component that takes 'shopping' as a prop
const ShoppingComponent: React.FC<ShoppingComponentProps> = ({ shopping }) => {
    console.log('shopping', shopping);
    // 5. Use the 'useState' hook to manage the 'showModal' state
    const [showModal, setShowModal] = useState(false);

    // 6. Define the 'ShoppingSkeleton' component to render a loading skeleton
    const ShoppingSkeleton = () => (
        <>
            {Array.from({ length: 5 }).map((_, index) => (
                <div key={index} className="flex items-center space-x-4">
                    <div className="w-10 h-10 bg-gray-300 dark:bg-gray-700 rounded-full animate-pulse"></div>
                    <div className="flex-grow">
                        <div className="w-2/3 h-4 bg-gray-300 dark:bg-gray-700 rounded animate-pulse mb-2"></div>
                        <div className="w-1/2 h-4 bg-gray-300 dark:bg-gray-700 rounded animate-pulse"></div>
                    </div>
                </div>
            ))}
        </>
    );

    // 7. Render the 'ShoppingComponent'
    return (
        <div className="bg-white dark:bg-gray-800 shadow-lg rounded-lg p-4 mt-4">
            <div className="flex items-center">
                <h2 className="text-lg font-semibold flex-grow text-gray-900 dark:text-gray-100">Shopping Results</h2>
                <IconPlus className="w-4 h-4 cursor-pointer text-gray-500 dark:text-gray-400" onClick={() => setShowModal(true)} />
            </div>
            <div className="mt-4">
                {shopping.length === 0 ? (
                    <ShoppingSkeleton />
                ) : (
                    shopping.slice(0, 3).map((item, index) => (
                        <div key={index} className="flex items-center space-x-4 mb-4">
                            <div className="w-10 h-10 overflow-hidden flex-shrink-0">
                                <a href={item.link} target="_blank" rel="noopener noreferrer">
                                    <img src={item.imageUrl} alt={item.title} className="w-full h-full object-cover rounded-full" />
                                </a>
                            </div>
                            <div className="flex-grow">
                                <a href={item.link} target="_blank" rel="noopener noreferrer" className="font-semibold text-sm mb-1 hover:underline text-gray-900 dark:text-gray-100">{item.title}</a>
                                <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
                                    <span className="mr-1">{item.source}</span>
                                    <span className="text-yellow-500 mr-1">{'★'.repeat(Math.floor(item.rating))}</span>
                                    <span>({item.ratingCount})</span>
                                </div>
                                <p className="text-gray-900 dark:text-gray-100 font-semibold text-sm">{item.price}</p>
                            </div>
                        </div>
                    ))
                )}
            </div>
            {showModal && (
                <div className="fixed inset-0 flex items-center justify-center z-50">
                    <div className="fixed inset-0 bg-black opacity-10 transition-opacity" onClick={() => setShowModal(false)}></div>
                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-3xl w-full mx-auto overflow-hidden relative">
                        <div className="sticky top-0 bg-white dark:bg-gray-800 px-6 py-4 flex items-center justify-between border-b border-gray-200 dark:border-gray-700">
                            <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Shopping Results</h2>
                            <IconClose className="w-6 h-6 cursor-pointer text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition duration-150 ease-in-out" onClick={() => setShowModal(false)} />
                        </div>
                        <div className="overflow-y-auto p-6 space-y-6 max-h-[70vh]">
                            {shopping.map((item, index) => (
                                <div key={index} className="flex items-center space-x-6">
                                    <div className="w-24 h-24 overflow-hidden flex-shrink-0 rounded">
                                        <a href={item.link} target="_blank" rel="noopener noreferrer">
                                            <img src={item.imageUrl} alt={item.title} className="w-full h-full object-cover" />
                                        </a>
                                    </div>
                                    <div className="flex-grow">
                                        <a href={item.link} target="_blank" rel="noopener noreferrer" className="font-bold text-xl mb-2 hover:underline text-gray-900 dark:text-gray-100">{item.title}</a>
                                        <p className="text-gray-500 dark:text-gray-400 text-base mb-2">{item.source}</p>
                                        <div className="flex items-center mb-2">
                                            <span className="text-yellow-500 text-lg mr-1">{'★'.repeat(Math.floor(item.rating))}</span>
                                            <span className="text-gray-500 dark:text-gray-400 text-sm">{item.ratingCount}</span>
                                        </div>
                                        <p className="text-gray-900 dark:text-gray-100 font-bold text-lg mb-2">{item.price}</p>
                                        {item.delivery && <p className="text-gray-500 dark:text-gray-400 text-base">{item.delivery}</p>}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ShoppingComponent;