'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Sidebar, GithubLogo, NotePencil } from '@phosphor-icons/react';

export function Header() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    <>
      <header className="sticky top-0 z-[500] flex items-center justify-between w-full px-4 border-b h-14 shrink-0 dark:bg-slate-800 bg-white backdrop-blur-xl">
        <div className="flex items-center justify-end space-x-2">

          {/* <Sidebar size={24} /> */}
          <a href="./">
            <NotePencil size={24} />
          </a>
        </div>
        <span className="inline-flex items-center home-links whitespace-nowrap">
          <a href="https://developersdigest.tech" rel="noopener" target="_blank">
            <span className="block sm:inline text-lg sm:text-xl lg:text-2xl font-semibold dark:text-white text-black">answer <span className="linear-wipe">engine</span></span>
          </a>
        </span>
        <a
          target="_blank"
          href="https://git.new/answr"
          rel="noopener noreferrer"

        >
          <GithubLogo size={24} />
        </a>
      </header>
      {/* <Sidebar isOpen={isSidebarOpen} onClose={toggleSidebar} /> */}
    </>
  );
}

// const Sidebar = ({ isOpen, onClose }) => {
//   const [settings, setSettings] = useState({
//     model: 'groq-mixtral',
//     toggleSetting: false,
//     dropdownSetting: 'Option 1',
//     textChunkSize: 1000,
//     textChunkOverlap: 400,
//     similarityResults: 4,
//     pagesToScan: 10,
//   });

//   useEffect(() => {
//     const storedSettings = localStorage.getItem('settings');
//     if (storedSettings) {
//       setSettings(JSON.parse(storedSettings));
//     }
//   }, []);

//   useEffect(() => {
//     localStorage.setItem('settings', JSON.stringify(settings));
//   }, [settings]);

//   const handleSettingsChange = (field, value) => {
//     setSettings((prevSettings) => ({
//       ...prevSettings,
//       [field]: value,
//     }));
//   };

//   return (
//     <div
//       className={`fixed inset-y-0 left-0 z-40 w-64 bg-white dark:bg-gray-800 shadow-lg transition-transform duration-300 ease-in-out transform ${isOpen ? 'translate-x-0' : '-translate-x-full'
//         }`}
//     >
//       <div className="flex flex-col h-full">
//         <div className="flex items-center justify-between px-4 py-3 border-b">
//           <h2 className="text-lg font-semibold">Settings</h2>
//           <button
//             onClick={onClose}
//             className="text-gray-500 hover:text-gray-600 focus:outline-none"
//           >
//             <svg
//               className="w-6 h-6"
//               fill="none"
//               stroke="currentColor"
//               viewBox="0 0 24 24"
//               xmlns="http://www.w3.org/2000/svg"
//             >
//               <path
//                 strokeLinecap="round"
//                 strokeLinejoin="round"
//                 strokeWidth={2}
//                 d="M6 18L18 6M6 6l12 12"
//               />
//             </svg>
//           </button>
//         </div>
//         <div className="flex-1 px-4 py-6 overflow-y-auto">
//           <div className="mb-4">
//             <label className="block mb-2 font-semibold">Model</label>
//             <select
//               value={settings.model}
//               onChange={(e) => handleSettingsChange('model', e.target.value)}
//               className="w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
//             >
//               <option value="groq-mixtral">Groq: Mixtral</option>
//               <option value="groq-llama-2-70b">Groq: Llama 2 70B</option>
//               <option value="groq-gemma">Groq: Gemma</option>
//             </select>
//           </div>
//           <div className="mb-4">
//             <label className="block mb-2 font-semibold">Model</label>
//             <select
//               value={settings.model}
//               onChange={(e) => handleSettingsChange('model', e.target.value)}
//               className="w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
//             >
//               <option value="groq-mixtral">Groq: Mixtral</option>
//               <option value="groq-llama-2-70b">Groq: Llama 2 70B</option>
//               <option value="groq-gemma">Groq: Gemma</option>
//             </select>
//           </div>
//           <div className="mb-4">
//             <label className="block mb-2 font-semibold">Model for Follow Up questions</label>
//             <select
//               value={settings.model}
//               onChange={(e) => handleSettingsChange('model', e.target.value)}
//               className="w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
//             >
//               <option value="groq-mixtral">Groq: Mixtral</option>
//               <option value="groq-llama-2-70b">Groq: Llama 2 70B</option>
//               <option value="groq-gemma">Groq: Gemma</option>
//             </select>
//           </div>
//           <div className="mb-4">
//             <label className="block mb-2 font-semibold">Model for Function Calling</label>
//             <select
//               value={settings.model}
//               onChange={(e) => handleSettingsChange('model', e.target.value)}
//               className="w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
//             >
//               <option value="groq-mixtral">Groq: Mixtral</option>
//               <option value="groq-llama-2-70b">Groq: Llama 2 70B</option>
//               <option value="groq-gemma">Groq: Gemma</option>
//             </select>
//           </div>
//           <div className="mb-4">
//             <label className="block mb-2 font-semibold">Show Sources in UI</label>
//             <div className="relative inline-block w-10 mr-2 align-middle select-none">
//               <input
//                 type="checkbox"
//                 checked={settings.toggleSetting}
//                 onChange={(e) => handleSettingsChange('toggleSetting', e.target.checked)}
//                 className="absolute block w-6 h-6 bg-white border-4 rounded-full appearance-none cursor-pointer"
//               />
//               <label className="block h-6 overflow-hidden bg-gray-300 rounded-full cursor-pointer"></label>
//             </div>
//           </div>
//           <div className="mb-4">
//             <h3 className="mb-2 font-semibold">Advanced Options</h3>
//             <div className="mb-4">
//               <label className="block mb-2 font-semibold">
//                 Text Chunk Size: {settings.textChunkSize}
//               </label>
//               <input
//                 type="range"
//                 min="500"
//                 max="2000"
//                 step="100"
//                 value={settings.textChunkSize}
//                 onChange={(e) => handleSettingsChange('textChunkSize', Number(e.target.value))}
//                 className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
//               />
//             </div>
//             <div className="mb-4">
//               <label className="block mb-2 font-semibold">
//                 Text Chunk Overlap: {settings.textChunkOverlap}
//               </label>
//               <input
//                 type="range"
//                 min="200"
//                 max="800"
//                 step="100"
//                 value={settings.textChunkOverlap}
//                 onChange={(e) => handleSettingsChange('textChunkOverlap', Number(e.target.value))}
//                 className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
//               />
//             </div>
//             <div className="mb-4">
//               <label className="block mb-2 font-semibold">
//                 Number of Similarity Results: {settings.similarityResults}
//               </label>
//               <input
//                 type="range"
//                 min="2"
//                 max="10"
//                 step="1"
//                 value={settings.similarityResults}
//                 onChange={(e) => handleSettingsChange('similarityResults', Number(e.target.value))}
//                 className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
//               />
//             </div>
//             <div className="mb-4">
//               <label className="block mb-2 font-semibold">
//                 Number of Pages to Scan: {settings.pagesToScan}
//               </label>
//               <input
//                 type="range"
//                 min="1"
//                 max="10"
//                 step="1"
//                 value={settings.pagesToScan}
//                 onChange={(e) => handleSettingsChange('pagesToScan', Number(e.target.value))}
//                 className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
//               />
//             </div>
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default Sidebar;