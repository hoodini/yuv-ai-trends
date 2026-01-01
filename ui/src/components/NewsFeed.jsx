import React, { useState } from 'react';
import NewsCard from './NewsCard';
import { motion, AnimatePresence } from 'framer-motion';
import { Code, BookOpen, Box, Layers } from 'lucide-react';
import { clsx } from 'clsx';

const NewsFeed = ({ items }) => {
    const [activeTab, setActiveTab] = useState('all');

    if (!items || items.length === 0) return null;

    const tabs = [
        { id: 'all', label: 'ALL PULSE', icon: Layers },
        { id: 'github_trending', label: 'CODE REPOS', icon: Code },
        { id: 'huggingface_papers', label: 'RESEARCH', icon: BookOpen },
        { id: 'huggingface_spaces', label: 'LIVE SPACES', icon: Box },
    ];

    const filteredItems = activeTab === 'all'
        ? items
        : items.filter(item => item.source === activeTab);

    return (
        <div className="w-full max-w-7xl mx-auto px-4 md:px-8 pb-20">

            {/* Tabs */}
            <div className="flex flex-wrap gap-2 mb-8 border-b border-white/10 pb-4">
                {tabs.map((tab) => {
                    const Icon = tab.icon;
                    const isActive = activeTab === tab.id;
                    return (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={clsx(
                                "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-mono tracking-wider transition-all duration-300",
                                isActive
                                    ? "bg-white/10 text-white border border-white/20 shadow-[0_0_10px_rgba(255,255,255,0.1)]"
                                    : "text-muted-foreground hover:text-white hover:bg-white/5"
                            )}
                        >
                            <Icon className="w-4 h-4" />
                            {tab.label}
                        </button>
                    );
                })}
            </div>

            {/* Grid */}
            <motion.div
                layout
                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            >
                <AnimatePresence mode="popLayout">
                    {filteredItems.map((item, index) => (
                        <motion.div
                            key={item.url}
                            layout
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.9 }}
                            transition={{ duration: 0.3 }}
                            className="h-full"
                        >
                            <NewsCard item={item} />
                        </motion.div>
                    ))}
                </AnimatePresence>
            </motion.div>

            {filteredItems.length === 0 && (
                <div className="py-20 text-center text-muted-foreground font-mono">
                    NO SIGNAL DETECTED IN THIS SECTOR
                </div>
            )}
        </div>
    );
};

export default NewsFeed;
