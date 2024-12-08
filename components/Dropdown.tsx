"use client";

import {useEffect, useRef} from 'react';
import {AnimatePresence, motion} from 'framer-motion';

type DropdownProps = {
    label: string;
    options: { value: string | number; label: string }[];
    selected: string | number;
    onSelect: (val: string | number) => void;
    isOpen: boolean;
    onToggle: () => void;
};

export default function Dropdown({label, options, selected, onSelect, isOpen, onToggle}: DropdownProps) {
    const dropdownRef = useRef<HTMLDivElement>(null);
    const current = options.find(o => o.value === selected);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                if (isOpen) {
                    onToggle();
                }
            }
        };

        if (isOpen) {
            document.addEventListener('mousedown', handleClickOutside);
        }

        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [isOpen, onToggle]);

    return (
        <div ref={dropdownRef} className="relative inline-block text-left">
            <span className="font-medium text-gray-700 dark:text-gray-300 mr-2">{label}:</span>
            <button
                type="button"
                onClick={onToggle}
                className="py-2 px-4 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded shadow-sm hover:bg-gray-100 dark:hover:bg-gray-600 transition select-none relative z-50 text-gray-700 dark:text-gray-200"
            >
                {current ? current.label : 'All'}
            </button>
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{opacity: 0, scale: 0.95, y: -10}}
                        animate={{opacity: 1, scale: 1, y: 0}}
                        exit={{opacity: 0, scale: 0.95, y: -10}}
                        transition={{duration: 0.1}}
                        className="origin-top-left absolute mt-2 w-40 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded shadow-lg z-[9999]"
                    >
                        {options.map((opt) => (
                            <button
                                key={String(opt.value)}
                                type="button"
                                onClick={() => {
                                    onSelect(opt.value);
                                    onToggle();
                                }}
                                className="block w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 dark:text-gray-200 select-none"
                            >
                                {opt.label}
                            </button>
                        ))}
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
