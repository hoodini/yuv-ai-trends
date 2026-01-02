import React, { useState } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import Header from './components/Header';
import ControlPanel from './components/ControlPanel';
import NewsFeed from './components/NewsFeed';
import LoadingState from './components/LoadingState';
import TopHighlights from './components/TopHighlights';

function App() {
    const [timeRange, setTimeRange] = useState('daily');
    const [items, setItems] = useState([]);
    const [isGenerating, setIsGenerating] = useState(false);
    const [isPopulating, setIsPopulating] = useState(false);
    const [error, setError] = useState(null);
    const [hasGenerated, setHasGenerated] = useState(false);

    const handleGenerate = async () => {
        setIsGenerating(true);
        setError(null);
        setItems([]);

        try {
            const response = await axios.post('http://localhost:8000/api/generate', {
                time_range: timeRange,
                limit: 50,
                disable_ai: false
            });

            setItems(response.data.items);
            setHasGenerated(true);
        } catch (err) {
            console.error("Error generating digest:", err);
            setError("Failed to connect to the neural network. Please ensure the backend server is running.");
        } finally {
            setIsGenerating(false);
        }
    };

    const handlePopulateSummaries = async () => {
        if (items.length === 0) {
            setError("No items to populate. Please generate content first.");
            return;
        }

        setIsPopulating(true);
        setError(null);

        try {
            const response = await axios.post('http://localhost:8000/api/populate-summaries', {
                items: items,
                force_refresh: false
            });

            if (response.data.success) {
                // Re-fetch to get updated items with summaries
                const refreshResponse = await axios.post('http://localhost:8000/api/generate', {
                    time_range: timeRange,
                    limit: 50,
                    disable_ai: false
                });
                setItems(refreshResponse.data.items);
                
                // Show success message
                console.log(`Populated ${response.data.newly_populated} new summaries`);
            }
        } catch (err) {
            console.error("Error populating summaries:", err);
            setError("Failed to populate AI summaries. " + (err.response?.data?.detail || err.message));
        } finally {
            setIsPopulating(false);
        }
    };

    // Logic to extract Top 5 Highlights
    const getTopHighlights = (allItems) => {
        if (!allItems || allItems.length === 0) return [];

        // Helper to find top item by source
        const findTop = (source, excludeIds = []) => {
            return allItems.find(item => item.source === source && !excludeIds.includes(item.url));
        };

        const highlights = [];
        const usedUrls = [];

        // 1. Top Repo (Hero)
        const topRepo = findTop('github_trending', usedUrls);
        if (topRepo) {
            highlights.push(topRepo);
            usedUrls.push(topRepo.url);
        }

        // 2. Top Paper
        const topPaper = findTop('huggingface_papers', usedUrls);
        if (topPaper) {
            highlights.push(topPaper);
            usedUrls.push(topPaper.url);
        }

        // 3. Top Space
        const topSpace = findTop('huggingface_spaces', usedUrls);
        if (topSpace) {
            highlights.push(topSpace);
            usedUrls.push(topSpace.url);
        }

        // 4 & 5. Next Top Repos
        const nextRepos = allItems
            .filter(item => item.source === 'github_trending' && !usedUrls.includes(item.url))
            .slice(0, 2);

        highlights.push(...nextRepos);

        return highlights;
    };

    const topHighlights = getTopHighlights(items);
    // Filter out highlights from the main feed to avoid duplication? 
    // User asked for "Top section... below the rest". 
    // Usually "rest" implies excluding the top ones, but sometimes users want them in the list too.
    // Let's keep them in the main list for now so filtering works completely, 
    // or we can remove them. Let's keep them in the main feed as well for completeness when filtering.

    return (
        <div className="min-h-screen bg-background text-text selection:bg-primary/30 selection:text-white overflow-x-hidden">
            {/* Global Background Effects */}
            <div className="fixed inset-0 bg-[url('/noise.svg')] opacity-20 pointer-events-none z-0 mix-blend-overlay"></div>
            <div className="fixed inset-0 bg-gradient-radial from-surface via-background to-black pointer-events-none z-0"></div>

            {/* Animated Orbs */}
            <div className="fixed top-[-20%] left-[-10%] w-[500px] h-[500px] bg-primary/20 rounded-full blur-[120px] animate-float pointer-events-none"></div>
            <div className="fixed bottom-[-20%] right-[-10%] w-[600px] h-[600px] bg-secondary/20 rounded-full blur-[120px] animate-float pointer-events-none" style={{ animationDelay: '-3s' }}></div>

            <div className="relative z-10 flex flex-col min-h-screen">
                <Header />

                <main className="flex-grow flex flex-col gap-8 relative">
                    <ControlPanel
                        timeRange={timeRange}
                        setTimeRange={setTimeRange}
                        onGenerate={handleGenerate}
                        isGenerating={isGenerating}
                    />

                    <AnimatePresence mode="wait">
                        {error && (
                            <motion.div
                                initial={{ opacity: 0, y: -20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -20 }}
                                className="w-full max-w-7xl mx-auto px-4 md:px-8"
                            >
                                <div className="p-4 bg-red-500/10 border border-red-500/50 rounded-lg text-red-400 text-sm font-mono flex items-center gap-3 shadow-[0_0_20px_rgba(239,68,68,0.2)]">
                                    <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
                                    CRITICAL ERROR: {error}
                                </div>
                            </motion.div>
                        )}

                        {isGenerating ? (
                            <motion.div
                                key="loading"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                            >
                                <LoadingState />
                            </motion.div>
                        ) : (
                            <motion.div
                                key="feed"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                transition={{ duration: 0.5 }}
                            >
                                {hasGenerated && items.length > 0 && (
                                    <>
                                        <TopHighlights items={topHighlights} />
                                        <NewsFeed items={items} />
                                    </>
                                )}
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {!hasGenerated && !isGenerating && !error && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.5 }}
                            className="flex-grow flex flex-col items-center justify-center text-center p-8"
                        >
                            <div className="p-8 rounded-full border border-white/5 bg-white/5 backdrop-blur-3xl mb-6 shadow-glass">
                                <div className="w-4 h-4 bg-primary rounded-full animate-pulse shadow-neon-blue"></div>
                            </div>
                            <h2 className="text-3xl font-display font-bold text-white mb-2 tracking-wide">SYSTEM READY</h2>
                            <p className="text-muted-foreground font-mono text-sm tracking-widest uppercase">
                                Awaiting Operator Command
                            </p>
                        </motion.div>
                    )}
                </main>

                <footer className="py-8 text-center relative z-10 border-t border-white/5 bg-black/40 backdrop-blur-sm mt-20">
                    <div className="flex flex-col items-center gap-2">
                        <p className="text-xs text-muted-foreground/50 font-mono tracking-[0.3em] uppercase">
                            YUV.AI TRENDS • SYSTEM ID: 8X-292 • SECURE CONNECTION
                        </p>
                        <p className="text-[10px] text-primary/30 font-mono">
                            DESIGNED BY YUVAL AVIDANI
                        </p>
                    </div>
                </footer>
            </div>
        </div>
    );
}

export default App;
