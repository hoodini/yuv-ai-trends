import React from 'react';
import { motion } from 'framer-motion';
import NewsCard from './NewsCard';
import { Trophy, Flame, Star, Zap } from 'lucide-react';

const TopHighlights = ({ items }) => {
    if (!items || items.length === 0) return null;

    // We expect items to be sorted by score/importance already
    // The first item is the "Hero"
    const heroItem = items[0];
    const subHeroItems = items.slice(1, 5);

    return (
        <div className="w-full max-w-7xl mx-auto px-4 md:px-8 mb-12">
            <div className="flex items-center gap-3 mb-6">
                <div className="p-2 bg-yellow-500/10 rounded-lg border border-yellow-500/20 shadow-[0_0_15px_rgba(234,179,8,0.2)]">
                    <Trophy className="w-6 h-6 text-yellow-500" />
                </div>
                <h2 className="text-2xl font-display font-bold text-white tracking-wide">
                    DAILY INTELLIGENCE BRIEFING
                </h2>
                <div className="h-px flex-grow bg-gradient-to-r from-yellow-500/50 to-transparent ml-4"></div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Hero Card (Takes up 2 columns on large screens) */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                    className="lg:col-span-2 h-full"
                >
                    <div className="relative h-full group">
                        <div className="absolute -inset-0.5 bg-gradient-to-r from-yellow-500 via-orange-500 to-red-500 rounded-2xl opacity-75 blur-lg group-hover:opacity-100 transition duration-500"></div>
                        <div className="relative h-full bg-black/80 backdrop-blur-xl rounded-2xl border border-yellow-500/30 p-1">
                            <div className="absolute top-4 right-4 z-20 flex items-center gap-1 px-3 py-1 bg-yellow-500 text-black font-bold text-xs rounded-full shadow-lg">
                                <Flame className="w-3 h-3 fill-black" /> #1 TRENDING
                            </div>
                            <NewsCard item={heroItem} isHero={true} />
                        </div>
                    </div>
                </motion.div>

                {/* Sub-Hero Grid (Right column) */}
                <div className="grid grid-cols-1 gap-6">
                    {subHeroItems.map((item, index) => (
                        <motion.div
                            key={item.url}
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.5, delay: (index + 1) * 0.1 }}
                            className="h-full"
                        >
                            <div className="relative h-full group">
                                <div className="absolute -inset-0.5 bg-gradient-to-r from-primary/50 to-secondary/50 rounded-2xl opacity-0 group-hover:opacity-50 blur-md transition duration-300"></div>
                                <NewsCard item={item} />
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default TopHighlights;
