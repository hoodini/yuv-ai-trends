import React from 'react';
import { motion } from 'framer-motion';

const LoadingState = () => {
    return (
        <div className="w-full h-96 flex flex-col items-center justify-center gap-8 relative overflow-hidden">
            {/* Background Effects */}
            <div className="absolute inset-0 bg-grid-animate opacity-20 mask-radial"></div>

            <div className="relative w-32 h-32">
                {/* Outer Ring */}
                <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
                    className="absolute inset-0 border border-primary/20 rounded-full border-t-primary shadow-[0_0_15px_rgba(0,240,255,0.2)]"
                />

                {/* Middle Ring */}
                <motion.div
                    animate={{ rotate: -360 }}
                    transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
                    className="absolute inset-4 border border-secondary/30 rounded-full border-b-secondary shadow-[0_0_15px_rgba(112,0,255,0.2)]"
                />

                {/* Inner Core */}
                <motion.div
                    animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className="absolute inset-10 bg-gradient-to-br from-primary to-secondary rounded-full blur-md"
                />
            </div>

            <div className="text-center z-10 space-y-2">
                <motion.h3
                    animate={{ opacity: [0.5, 1, 0.5] }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className="text-2xl font-display font-bold text-white tracking-widest uppercase text-glow"
                >
                    Establishing Uplink
                </motion.h3>

                <div className="flex flex-col items-center gap-1">
                    <p className="text-xs font-mono text-primary/70 tracking-[0.2em] uppercase">
                        Scanning Global Neural Networks
                    </p>
                    <div className="flex gap-1 mt-2">
                        {[...Array(3)].map((_, i) => (
                            <motion.div
                                key={i}
                                animate={{ height: [4, 12, 4] }}
                                transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }}
                                className="w-1 bg-primary rounded-full"
                            />
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LoadingState;
