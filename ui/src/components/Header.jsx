import React, { useState } from 'react';
import { Cpu, Activity, Wifi, Settings, Rss, Menu, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import SettingsModal from './Settings';
import { API_URL } from '../config';

// RSS Feed URL
const RSS_URL = `${API_URL}/rss.xml`;

const Header = () => {
    const [settingsOpen, setSettingsOpen] = useState(false);
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    return (
        <>
        <motion.header
            initial={{ y: -100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="w-full py-4 px-6 fixed top-0 z-50 bg-background/80 backdrop-blur-md border-b border-white/5"
        >
            <div className="max-w-7xl mx-auto flex justify-between items-center">
                {/* Logo Section */}
                <div className="flex items-center gap-4">
                    <motion.div
                        whileHover={{ rotate: 180, scale: 1.1 }}
                        transition={{ duration: 0.5 }}
                        className="p-2 bg-primary/10 rounded-lg border border-primary/50 shadow-neon-blue"
                    >
                        <Cpu className="w-6 h-6 text-primary" />
                    </motion.div>

                    <div className="flex flex-col">
                        <h1 className="text-2xl font-display font-bold tracking-wider text-white">
                            <span className="text-primary text-glow">YUV</span>.AI
                        </h1>
                        <div className="flex items-center gap-2 text-[10px] font-mono text-primary/60 tracking-[0.2em] uppercase">
                            <span>Neural Nexus</span>
                            <span className="w-1 h-1 bg-primary rounded-full animate-pulse"></span>
                            <span>Online</span>
                        </div>
                    </div>
                </div>

                {/* Mobile Menu Button */}
                <div className="flex md:hidden items-center gap-2">
                    <motion.a
                        href={RSS_URL}
                        target="_blank"
                        rel="noopener noreferrer"
                        whileTap={{ scale: 0.95 }}
                        className="p-2 rounded-lg border border-orange-500/30 bg-orange-500/10"
                        title="RSS Feed"
                    >
                        <Rss className="w-5 h-5 text-orange-400" />
                    </motion.a>
                    <motion.button
                        whileTap={{ scale: 0.95 }}
                        onClick={() => setSettingsOpen(true)}
                        className="p-2 rounded-lg border border-white/10 bg-white/5"
                    >
                        <Settings className="w-5 h-5 text-muted-foreground" />
                    </motion.button>
                </div>

                {/* HUD Elements - Desktop */}
                <div className="hidden md:flex items-center gap-8">
                    <div className="flex items-center gap-3 font-mono text-xs text-muted-foreground">
                        <Activity className="w-4 h-4 text-secondary animate-pulse" />
                        <span>SYSTEM STATUS: OPTIMAL</span>
                    </div>

                    <div className="h-8 w-px bg-gradient-to-b from-transparent via-white/20 to-transparent"></div>

                    <div className="flex items-center gap-3 font-mono text-xs text-muted-foreground">
                        <Wifi className="w-4 h-4 text-neon-green" />
                        <span>NETLINK: SECURE</span>
                    </div>

                    <div className="px-3 py-1 rounded border border-white/10 bg-white/5 text-[10px] font-mono text-white/50">
                        v2.5.0-CYBER
                    </div>

                    <div className="h-8 w-px bg-gradient-to-b from-transparent via-white/20 to-transparent"></div>

                    <motion.a
                        href={RSS_URL}
                        target="_blank"
                        rel="noopener noreferrer"
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className="flex items-center gap-2 px-3 py-2 rounded-lg border border-orange-500/30 bg-orange-500/10 hover:bg-orange-500/20 transition-colors group"
                        title="Subscribe via RSS"
                    >
                        <Rss className="w-4 h-4 text-orange-400 group-hover:text-orange-300 transition-all duration-300" />
                        <span className="text-xs font-mono text-orange-400 group-hover:text-orange-300">RSS</span>
                    </motion.a>

                    <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => setSettingsOpen(true)}
                        className="p-2 rounded-lg border border-white/10 bg-white/5 hover:bg-white/10 transition-colors group"
                        title="Settings"
                    >
                        <Settings className="w-5 h-5 text-muted-foreground group-hover:text-white group-hover:rotate-90 transition-all duration-300" />
                    </motion.button>
                </div>
            </div>
        </motion.header>

        <SettingsModal isOpen={settingsOpen} onClose={() => setSettingsOpen(false)} />
        </>
    );
};

export default Header;
