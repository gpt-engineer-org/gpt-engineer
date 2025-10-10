"use client";
import { useState } from 'react';
const RateLimit = () => {
    const [isOpen, setIsOpen] = useState(true);
    const handleClose = () => {
        setIsOpen(false);
    };
    const handleClickOutside = (event: React.MouseEvent<HTMLDivElement>) => {
        if ((event.target as HTMLElement).classList.contains('modal-overlay')) {
            handleClose();
        }
    };
    if (!isOpen) return null;
    return (
        <div
            className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-50 modal-overlay rate-limit-modal"
            onClick={handleClickOutside}
        >
            <div className="dark:bg-slate-800 bg-white shadow-lg rounded-lg p-6 max-w-md mx-auto">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-semibold dark:text-white text-black">
                        Rate Limit Reached
                    </h2>
                    <button
                        className="text-gray-500 hover:text-gray-700 focus:outline-none"
                        onClick={handleClose}
                    >
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            className="h-6 w-6"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M6 18L18 6M6 6l12 12"
                            />
                        </svg>
                    </button>
                </div>
                <p className="text-gray-600 dark:text-gray-400 text-lg">
                    You have reached the rate limit for the current period. Please try again soon!
                </p>
                <div className="text-sm">
                    <p className="text-sm">Rate limiting powered by Upstash   <svg className="inline m-2" height="20" viewBox="0 0 354 472" fill="none" xmlns="http://www.w3.org/2000/svg"><g clipPath="url(#clip0_39_147)"><path d="M0.421875 412.975C78.5269 491.079 205.16 491.079 283.265 412.975C361.369 334.87 361.369 208.237 283.265 130.132L247.909 165.487C306.488 224.066 306.488 319.041 247.909 377.619C189.331 436.198 94.3559 436.198 35.7769 377.619L0.421875 412.975Z" fill="#34D399"></path><path d="M71.1328 342.264C110.185 381.316 173.501 381.316 212.554 342.264C251.606 303.212 251.606 239.895 212.554 200.843L177.199 236.198C196.725 255.724 196.725 287.382 177.199 306.909C157.672 326.435 126.014 326.435 106.488 306.909L71.1328 342.264Z" fill="#34D399"></path><path d="M353.974 59.421C275.869 -18.6835 149.236 -18.6835 71.1315 59.421C-6.97352 137.526 -6.97352 264.159 71.1315 342.264L106.486 306.909C47.9085 248.33 47.9085 153.355 106.486 94.777C165.065 36.198 260.04 36.198 318.618 94.777L353.974 59.421Z" fill="#6EE7B7"></path><path d="M283.264 130.132C244.212 91.08 180.894 91.08 141.842 130.132C102.789 169.185 102.789 232.501 141.842 271.553L177.197 236.198C157.671 216.672 157.671 185.014 177.197 165.487C196.723 145.961 228.381 145.961 247.908 165.487L283.264 130.132Z" fill="#6EE7B7"></path></g><defs><clipPath id="clip0_39_147"><rect width="354" height="472" fill="white"></rect></clipPath></defs></svg></p>
                </div>
            </div>
        </div>
    );
};
export default RateLimit;