import React from 'react';
import { RefreshCw, Zap, Clock, Calendar, Globe } from 'lucide-react';
import { motion } from 'framer-motion';
import { clsx } from 'clsx';

const ControlPanel = ({ timeRange, setTimeRange, onGenerate, isGenerating }) => {
    const ranges = [
        { id: 'daily', label: '24H PROTOCOL', icon: Clock },
        { id: 'weekly', label: '7-DAY DIGEST', icon: Calendar },
        { id: 'monthly', label: '30-DAY REPORT', icon: Globe },
    ];

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="w-full max-w-7xl mx-auto px-4 md:px-8 py-12 mt-20"
        >
            <div className="relative p-[1px] rounded-2xl bg-gradient-to-r from-primary/20 via-secondary/20 to-primary/20">
                <div className="absolute inset-0 bg-gradient-to-r from-primary/10 via-secondary/10 to-primary/10 blur-xl opacity-50"></div>

                <div className="relative bg-surface/90 backdrop-blur-xl rounded-2xl p-6 md:p-8 flex flex-col md:flex-row justify-between items-center gap-8 overflow-hidden">

                    {/* Decorative Grid Background */}
                    <div className="absolute inset-0 bg-[url('/noise.svg')] opacity-5 pointer-events-none"></div>
                    <div className="absolute inset-0 bg-grid-animate opacity-10 pointer-events-none"></div>

                    {/* Time Selector */}
                    <div className="flex flex-col gap-3 w-full md:w-auto z-10">
                        <label className="text-xs text-primary font-mono tracking-[0.2em] uppercase flex items-center gap-2">
                            <span className="w-2 h-2 bg-primary rounded-full animate-pulse"></span>
                            Temporal Scope
                        </label>
                        <div className="flex p-1 bg-black/60 rounded-xl border border-white/10 backdrop-blur-md">
                            {ranges.map((range) => {
                                const Icon = range.icon;
                                const isActive = timeRange === range.id;
                                return (
                                    <button
                                        key={range.id}
                                        onClick={() => setTimeRange(range.id)}
                                        className={clsx(
                                            "relative px-6 py-3 rounded-lg text-sm font-display font-bold transition-all duration-300 flex items-center gap-2 flex-1 md:flex-none justify-center overflow-hidden group",
                                            isActive
                                                ? "text-black shadow-[0_0_20px_rgba(0,240,255,0.3)]"
                                                : "text-muted-foreground hover:text-white"
                                        )}
                                    >
                                        {isActive && (
                                            <motion.div
                                                layoutId="activeTab"
                                                className="absolute inset-0 bg-primary"
                                                transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                                            />
                                        )}
                                        <span className="relative z-10 flex items-center gap-2">
                                            <Icon className="w-4 h-4" />
                                            {range.label}
                                        </span>
                                    </button>
                                );
                            })}
                        </div>
                    </div>

                    {/* Action Button */}
                    <div className="w-full md:w-auto z-10">
                        <button
                            onClick={onGenerate}
                            disabled={isGenerating}
                            className={clsx(
                                "group relative w-full md:w-auto px-10 py-4 bg-transparent overflow-hidden rounded-xl transition-all duration-300",
                                isGenerating ? "cursor-wait" : "hover:scale-105 active:scale-95"
                            )}
                        >
                            {/* Button Background & Glow */}
                            <div className="absolute inset-0 bg-gradient-to-r from-secondary to-accent opacity-80 group-hover:opacity-100 transition-opacity"></div>
                            <div className="absolute inset-0 bg-[url('/noise.svg')] opacity-20"></div>

                            {/* Content */}
                            <div className="relative flex items-center justify-center gap-3 font-display font-bold text-white tracking-wider">
                                {isGenerating ? (
                                    <>
                                        <RefreshCw className="w-5 h-5 animate-spin" />
                                        <span>INITIALIZING SCAN...</span>
                                    </>
                                ) : (
                                    <>
                                        <Zap className="w-5 h-5 group-hover:text-yellow-300 transition-colors" />
                                        <span>INITIATE SEQUENCE</span>
                                    </>
                                )}
                            </div>

                            {/* Border Glow */}
                            <div className="absolute inset-0 border border-white/20 rounded-xl group-hover:border-white/50 transition-colors"></div>
                        </button>
                    </div>

                </div>
            </div>
        </motion.div>
    );
};

export default ControlPanel;
