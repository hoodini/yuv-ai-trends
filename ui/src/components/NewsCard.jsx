import React, { useState } from 'react';
import { Star, ExternalLink, BookOpen, Box, MessageSquare, Copy, Check, Share2, Code } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const NewsCard = ({ item }) => {
    const [isHovered, setIsHovered] = useState(false);
    const [copied, setCopied] = useState(false);

    const handleCopy = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (item.ai_summary) {
            navigator.clipboard.writeText(item.ai_summary);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    const getIcon = () => {
        switch (item.source) {
            case 'github_trending': return <Code className="w-4 h-4 text-primary" />;
            case 'huggingface_papers': return <BookOpen className="w-4 h-4 text-secondary" />;
            case 'huggingface_spaces': return <Box className="w-4 h-4 text-accent" />;
            default: return <Box className="w-4 h-4" />;
        }
    };

    const getSourceColor = () => {
        switch (item.source) {
            case 'github_trending': return 'text-primary border-primary/30 bg-primary/10';
            case 'huggingface_papers': return 'text-secondary border-secondary/30 bg-secondary/10';
            case 'huggingface_spaces': return 'text-accent border-accent/30 bg-accent/10';
            default: return 'text-white border-white/30 bg-white/10';
        }
    };

    return (
        <motion.a
            href={item.url}
            target="_blank"
            rel="noopener noreferrer"
            className="group relative block h-full perspective-1000"
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
            whileHover={{ scale: 1.02, rotateX: 2, rotateY: 2 }}
            transition={{ type: "spring", stiffness: 400, damping: 30 }}
        >
            {/* Holographic Glow Background */}
            <div className="absolute -inset-0.5 bg-gradient-to-r from-primary via-secondary to-accent rounded-2xl opacity-0 group-hover:opacity-70 blur-lg transition duration-500 group-hover:duration-200 animate-tilt"></div>

            <div className="relative h-full bg-surface border border-white/10 rounded-2xl p-6 flex flex-col gap-4 overflow-hidden backdrop-blur-xl">

                {/* Grid Overlay */}
                <div className="absolute inset-0 bg-[url('/noise.svg')] opacity-5 pointer-events-none"></div>
                <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"></div>

                {/* Header */}
                <div className="flex justify-between items-start z-10">
                    <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-[10px] font-mono uppercase tracking-wider border ${getSourceColor()}`}>
                        {getIcon()}
                        <span>{item.source.replace('_', ' ')}</span>
                    </div>

                    <div className="flex items-center gap-3">
                        {(item.stars || item.likes) && (
                            <div className="flex items-center gap-1.5 font-mono text-xs text-yellow-400">
                                <Star className="w-3 h-3 fill-current" />
                                <span>{(item.stars || item.likes).toLocaleString()}</span>
                            </div>
                        )}
                        <motion.div
                            whileHover={{ rotate: 45 }}
                            className="p-1 rounded-full bg-white/5 group-hover:bg-white/10 transition-colors"
                        >
                            <ExternalLink className="w-4 h-4 text-muted-foreground group-hover:text-white" />
                        </motion.div>
                    </div>
                </div>

                {/* Content */}
                <div className="z-10 flex-grow">
                    <h3 className="text-xl font-display font-bold text-white group-hover:text-primary transition-colors line-clamp-2 mb-3 leading-tight">
                        {item.name}
                    </h3>
                    <p className="text-sm text-muted-foreground line-clamp-3 mb-4 font-sans leading-relaxed group-hover:text-gray-300 transition-colors">
                        {item.description}
                    </p>

                    {/* Tags */}
                    <div className="flex flex-wrap gap-2">
                        {item.language && (
                            <span className="px-2 py-1 rounded text-[10px] font-mono bg-primary/5 text-primary border border-primary/20">
                                {item.language}
                            </span>
                        )}
                        {item.sdk && (
                            <span className="px-2 py-1 rounded text-[10px] font-mono bg-secondary/5 text-secondary border border-secondary/20">
                                {item.sdk}
                            </span>
                        )}
                    </div>
                </div>

                {/* AI Insight Section */}
                <AnimatePresence>
                    {item.ai_summary && (
                        <motion.div
                            initial={{ height: "auto", opacity: 0.8 }}
                            whileHover={{ opacity: 1 }}
                            className="relative mt-auto pt-4 border-t border-white/5 z-10"
                        >
                            <div className="relative p-4 rounded-xl bg-gradient-to-br from-white/5 to-transparent border border-white/5 group-hover:border-primary/30 transition-all duration-300 overflow-hidden">
                                {/* Scanning Line Animation */}
                                <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-primary to-transparent opacity-0 group-hover:opacity-50 animate-scan"></div>

                                <div className="flex justify-between items-center mb-3">
                                    <span className="text-[10px] uppercase tracking-widest text-primary font-bold flex items-center gap-2">
                                        <MessageSquare className="w-3 h-3" />
                                        Practical Analysis
                                    </span>
                                    <button
                                        onClick={handleCopy}
                                        className="text-muted-foreground hover:text-white transition-colors p-1 hover:bg-white/10 rounded"
                                        title="Copy analysis"
                                    >
                                        {copied ? <Check className="w-3 h-3 text-neon-green" /> : <Copy className="w-3 h-3" />}
                                    </button>
                                </div>

                                <div className="space-y-2.5 text-xs leading-relaxed font-sans">
                                    {/* Parse and display structured content */}
                                    {item.ai_summary.split('\n\n').map((section, idx) => {
                                        const [label, ...content] = section.split(':');
                                        const text = content.join(':').trim();

                                        // Determine color based on section
                                        let labelColor = 'text-primary';
                                        if (label.includes('Solves')) labelColor = 'text-secondary';
                                        if (label.includes('How')) labelColor = 'text-accent';

                                        return (
                                            <div key={idx} className="flex gap-2">
                                                <span className={`font-bold ${labelColor} shrink-0`}>
                                                    {label.replace(/\*/g, '')}:
                                                </span>
                                                <span className="text-gray-300">
                                                    {text.replace(/\*/g, '')}
                                                </span>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

            </div>
        </motion.a>
    );
};

export default NewsCard;
