import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Key, Settings as SettingsIcon, Check, AlertCircle, Eye, EyeOff, Trash2, ExternalLink, Zap } from 'lucide-react';
import axios from 'axios';
import { API_URL } from '../App';

// LocalStorage keys
const STORAGE_KEYS = {
    PROVIDER: 'yuv_ai_provider',
    MODEL: 'yuv_ai_model',
    API_KEYS: 'yuv_ai_keys'
};

// Helper functions for localStorage
export const getStoredSettings = () => {
    try {
        return {
            provider: localStorage.getItem(STORAGE_KEYS.PROVIDER) || 'local_wasm',
            model: localStorage.getItem(STORAGE_KEYS.MODEL) || '',
            apiKeys: JSON.parse(localStorage.getItem(STORAGE_KEYS.API_KEYS) || '{}')
        };
    } catch {
        return { provider: 'local_wasm', model: '', apiKeys: {} };
    }
};

export const saveStoredSettings = (settings) => {
    try {
        if (settings.provider) localStorage.setItem(STORAGE_KEYS.PROVIDER, settings.provider);
        if (settings.model !== undefined) localStorage.setItem(STORAGE_KEYS.MODEL, settings.model);
        if (settings.apiKeys) localStorage.setItem(STORAGE_KEYS.API_KEYS, JSON.stringify(settings.apiKeys));
    } catch (e) {
        console.error('Failed to save settings:', e);
    }
};

export const getApiKeyForProvider = (provider) => {
    const settings = getStoredSettings();
    return settings.apiKeys[provider] || '';
};

const Settings = ({ isOpen, onClose }) => {
    const [serverSettings, setServerSettings] = useState(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('providers');
    
    // Local state for editing
    const [selectedProvider, setSelectedProvider] = useState('local_wasm');
    const [selectedModel, setSelectedModel] = useState('');
    const [apiKeys, setApiKeys] = useState({});
    const [showKeys, setShowKeys] = useState({});
    const [validating, setValidating] = useState({});
    const [errors, setErrors] = useState({});
    const [success, setSuccess] = useState({});

    useEffect(() => {
        if (isOpen) {
            fetchSettings();
            loadLocalSettings();
        }
    }, [isOpen]);

    const loadLocalSettings = () => {
        const stored = getStoredSettings();
        setSelectedProvider(stored.provider);
        setSelectedModel(stored.model);
    };

    const fetchSettings = async () => {
        try {
            setLoading(true);
            const response = await axios.get(`${API_URL}/api/settings`);
            setServerSettings(response.data);
        } catch (err) {
            console.error('Error fetching settings:', err);
            setErrors({ general: 'Failed to load settings from server' });
        } finally {
            setLoading(false);
        }
    };

    const handleValidateKey = async (provider) => {
        const apiKey = apiKeys[provider];
        if (!apiKey || !apiKey.trim()) {
            setErrors({ ...errors, [provider]: 'Please enter an API key' });
            return;
        }

        setValidating({ ...validating, [provider]: true });
        setErrors({ ...errors, [provider]: null });
        setSuccess({ ...success, [provider]: null });

        try {
            const response = await axios.post(`${API_URL}/api/validate-key`, {
                provider,
                api_key: apiKey
            });

            if (response.data.valid) {
                // Save to localStorage
                const stored = getStoredSettings();
                stored.apiKeys[provider] = apiKey;
                saveStoredSettings(stored);
                
                setSuccess({ ...success, [provider]: 'API key saved to your browser!' });
                setApiKeys({ ...apiKeys, [provider]: '' });
            } else {
                setErrors({ ...errors, [provider]: response.data.message });
            }
        } catch (err) {
            setErrors({
                ...errors,
                [provider]: err.response?.data?.detail || 'Failed to validate API key'
            });
        } finally {
            setValidating({ ...validating, [provider]: false });
        }
    };

    const handleDeleteKey = (provider) => {
        const stored = getStoredSettings();
        delete stored.apiKeys[provider];
        saveStoredSettings(stored);
        setSuccess({ ...success, [provider]: 'API key removed from your browser' });
        
        if (stored.provider === provider) {
            stored.provider = 'local_wasm';
            saveStoredSettings(stored);
            setSelectedProvider('local_wasm');
        }
    };

    const handleSaveProvider = () => {
        const stored = getStoredSettings();
        
        const providerInfo = serverSettings?.available_providers?.[selectedProvider];
        if (providerInfo?.requiresKey && !stored.apiKeys[selectedProvider]) {
            setErrors({ provider: `Please add an API key for ${providerInfo.name} first` });
            return;
        }
        
        stored.provider = selectedProvider;
        stored.model = selectedModel;
        saveStoredSettings(stored);
        
        setSuccess({ provider: `Switched to ${providerInfo?.name || selectedProvider}` });
        setErrors({ ...errors, provider: null });
    };

    const hasStoredKey = (provider) => {
        const stored = getStoredSettings();
        return !!stored.apiKeys[provider];
    };

    if (!isOpen) return null;

    return (
        <AnimatePresence>
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
                onClick={onClose}
            >
                <motion.div
                    initial={{ scale: 0.95, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    exit={{ scale: 0.95, opacity: 0 }}
                    className="bg-surface border border-white/10 rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden shadow-2xl"
                    onClick={(e) => e.stopPropagation()}
                >
                    {/* Header */}
                    <div className="flex items-center justify-between p-6 border-b border-white/10 bg-gradient-to-r from-primary/10 to-secondary/10">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-primary/20 rounded-lg">
                                <SettingsIcon className="w-6 h-6 text-primary" />
                            </div>
                            <div>
                                <h2 className="text-2xl font-display font-bold text-white">Settings</h2>
                                <p className="text-sm text-muted-foreground">Your settings are stored locally in your browser</p>
                            </div>
                        </div>
                        <button
                            onClick={onClose}
                            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                        >
                            <X className="w-5 h-5 text-muted-foreground" />
                        </button>
                    </div>

                    {/* Privacy Notice */}
                    <div className="mx-6 mt-4 p-3 bg-green-500/10 border border-green-500/30 rounded-lg flex items-center gap-3">
                        <Zap className="w-5 h-5 text-green-400 flex-shrink-0" />
                        <p className="text-xs text-green-400">
                            <strong>Privacy First:</strong> API keys are stored only in your browser's localStorage. They never leave your device except when making AI requests.
                        </p>
                    </div>

                    {/* Tabs */}
                    <div className="flex gap-1 p-4 bg-black/20 border-b border-white/5">
                        <button
                            onClick={() => setActiveTab('providers')}
                            className={`px-4 py-2 rounded-lg text-sm font-mono transition-all ${
                                activeTab === 'providers'
                                    ? 'bg-white/10 text-white'
                                    : 'text-muted-foreground hover:text-white hover:bg-white/5'
                            }`}
                        >
                            AI PROVIDER
                        </button>
                        <button
                            onClick={() => setActiveTab('api-keys')}
                            className={`px-4 py-2 rounded-lg text-sm font-mono transition-all ${
                                activeTab === 'api-keys'
                                    ? 'bg-white/10 text-white'
                                    : 'text-muted-foreground hover:text-white hover:bg-white/5'
                            }`}
                        >
                            API KEYS
                        </button>
                    </div>

                    {/* Content */}
                    <div className="p-6 overflow-y-auto max-h-[calc(90vh-280px)]">
                        {loading ? (
                            <div className="flex items-center justify-center py-12">
                                <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
                            </div>
                        ) : activeTab === 'providers' ? (
                            <ProvidersTab
                                serverSettings={serverSettings}
                                selectedProvider={selectedProvider}
                                setSelectedProvider={setSelectedProvider}
                                selectedModel={selectedModel}
                                setSelectedModel={setSelectedModel}
                                onSave={handleSaveProvider}
                                hasStoredKey={hasStoredKey}
                                error={errors.provider}
                                success={success.provider}
                            />
                        ) : (
                            <ApiKeysTab
                                serverSettings={serverSettings}
                                apiKeys={apiKeys}
                                setApiKeys={setApiKeys}
                                showKeys={showKeys}
                                setShowKeys={setShowKeys}
                                validating={validating}
                                errors={errors}
                                success={success}
                                onValidate={handleValidateKey}
                                onDelete={handleDeleteKey}
                                hasStoredKey={hasStoredKey}
                            />
                        )}
                    </div>
                </motion.div>
            </motion.div>
        </AnimatePresence>
    );
};

const ProvidersTab = ({ serverSettings, selectedProvider, setSelectedProvider, selectedModel, setSelectedModel, onSave, hasStoredKey, error, success }) => {
    const providers = serverSettings?.available_providers || {};
    const models = serverSettings?.models || {};
    const storedSettings = getStoredSettings();

    return (
        <div className="space-y-6">
            <div>
                <h3 className="text-lg font-bold text-white mb-4">Choose AI Provider</h3>
                <p className="text-sm text-muted-foreground mb-6">
                    Select which AI model generates summaries. Local Web LLM works without any API key!
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {Object.entries(providers).map(([key, provider]) => {
                        const needsKey = provider.requiresKey;
                        const hasKey = hasStoredKey(key);
                        const isActive = storedSettings.provider === key;

                        return (
                            <motion.button
                                key={key}
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                onClick={() => {
                                    setSelectedProvider(key);
                                    const defaultModel = models[key]?.find(m => m.recommended)?.id || models[key]?.[0]?.id || '';
                                    setSelectedModel(defaultModel);
                                }}
                                className={`p-4 rounded-xl border text-left transition-all relative ${
                                    selectedProvider === key
                                        ? 'border-primary bg-primary/10'
                                        : 'border-white/10 hover:border-white/20 bg-white/5'
                                }`}
                            >
                                {isActive && (
                                    <span className="absolute top-2 right-2 text-[10px] px-2 py-0.5 rounded bg-primary/30 text-primary font-mono">
                                        ACTIVE
                                    </span>
                                )}
                                <div className="flex items-start justify-between mb-2">
                                    <h4 className="font-bold text-white">{provider.name}</h4>
                                    {selectedProvider === key && (
                                        <Check className="w-5 h-5 text-primary" />
                                    )}
                                </div>
                                <p className="text-xs text-muted-foreground mb-3">{provider.description}</p>
                                <div className="flex items-center gap-2">
                                    {!needsKey ? (
                                        <span className="text-xs px-2 py-1 rounded bg-green-500/20 text-green-400">
                                            NO KEY NEEDED
                                        </span>
                                    ) : hasKey ? (
                                        <span className="text-xs px-2 py-1 rounded bg-green-500/20 text-green-400">
                                            KEY SAVED
                                        </span>
                                    ) : (
                                        <span className="text-xs px-2 py-1 rounded bg-yellow-500/20 text-yellow-400">
                                            NEEDS API KEY
                                        </span>
                                    )}
                                </div>
                            </motion.button>
                        );
                    })}
                </div>
            </div>

            {selectedProvider && models[selectedProvider] && models[selectedProvider].length > 1 && (
                <div>
                    <h3 className="text-lg font-bold text-white mb-4">Model Selection</h3>
                    <div className="grid grid-cols-1 gap-3">
                        {models[selectedProvider].map((model) => (
                            <button
                                key={model.id}
                                onClick={() => setSelectedModel(model.id)}
                                className={`p-3 rounded-lg border text-left transition-all ${
                                    selectedModel === model.id
                                        ? 'border-primary bg-primary/10'
                                        : 'border-white/10 hover:border-white/20 bg-white/5'
                                }`}
                            >
                                <div className="flex items-center justify-between">
                                    <div>
                                        <span className="text-white font-mono text-sm">{model.name}</span>
                                        {model.recommended && (
                                            <span className="ml-2 text-xs px-2 py-0.5 rounded bg-yellow-500/20 text-yellow-400">
                                                RECOMMENDED
                                            </span>
                                        )}
                                    </div>
                                    {selectedModel === model.id && (
                                        <Check className="w-4 h-4 text-primary" />
                                    )}
                                </div>
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {error && (
                <div className="p-3 bg-red-500/10 border border-red-500/50 rounded-lg text-red-400 text-sm flex items-center gap-2">
                    <AlertCircle className="w-4 h-4" />
                    {error}
                </div>
            )}

            {success && (
                <div className="p-3 bg-green-500/10 border border-green-500/50 rounded-lg text-green-400 text-sm flex items-center gap-2">
                    <Check className="w-4 h-4" />
                    {success}
                </div>
            )}

            <button
                onClick={onSave}
                className="w-full py-3 bg-primary hover:bg-primary/80 text-white font-bold rounded-lg transition-colors"
            >
                Save Provider Settings
            </button>
        </div>
    );
};

const ApiKeysTab = ({ serverSettings, apiKeys, setApiKeys, showKeys, setShowKeys, validating, errors, success, onValidate, onDelete, hasStoredKey }) => {
    const providers = serverSettings?.available_providers || {};

    const providerConfigs = [
        { key: 'groq', placeholder: 'gsk_...' },
        { key: 'cohere', placeholder: 'your-cohere-api-key' },
        { key: 'anthropic', placeholder: 'sk-ant-...' },
    ];

    return (
        <div className="space-y-6">
            <div>
                <h3 className="text-lg font-bold text-white mb-2">Your API Keys</h3>
                <p className="text-sm text-muted-foreground mb-6">
                    Add API keys to use premium AI providers. Keys are stored securely in your browser only.
                </p>
            </div>

            {providerConfigs.map((config) => {
                const provider = providers[config.key];
                if (!provider) return null;
                
                const hasKey = hasStoredKey(config.key);

                return (
                    <div key={config.key} className="p-4 bg-white/5 rounded-xl border border-white/10">
                        <div className="flex items-start justify-between mb-3">
                            <div>
                                <h4 className="font-bold text-white flex items-center gap-2">
                                    <Key className="w-4 h-4 text-primary" />
                                    {provider.name}
                                </h4>
                                <p className="text-xs text-muted-foreground mt-1">
                                    {hasKey ? '✓ API key saved in browser' : 'No API key configured'}
                                </p>
                            </div>
                            <div className="flex items-center gap-2">
                                {provider.keyUrl && (
                                    <a
                                        href={provider.keyUrl}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="p-2 hover:bg-white/10 rounded-lg transition-colors group"
                                        title="Get API key"
                                    >
                                        <ExternalLink className="w-4 h-4 text-muted-foreground group-hover:text-primary" />
                                    </a>
                                )}
                                {hasKey && (
                                    <button
                                        onClick={() => onDelete(config.key)}
                                        className="p-2 hover:bg-red-500/20 rounded-lg transition-colors group"
                                        title="Delete API key"
                                    >
                                        <Trash2 className="w-4 h-4 text-muted-foreground group-hover:text-red-400" />
                                    </button>
                                )}
                            </div>
                        </div>

                        <div className="space-y-3">
                            <div className="relative">
                                <input
                                    type={showKeys[config.key] ? 'text' : 'password'}
                                    value={apiKeys[config.key] || ''}
                                    onChange={(e) => setApiKeys({ ...apiKeys, [config.key]: e.target.value })}
                                    placeholder={hasKey ? '••••••••••••••••' : config.placeholder}
                                    className="w-full px-4 py-3 pr-10 bg-black/30 border border-white/10 rounded-lg text-white placeholder-muted-foreground focus:border-primary focus:outline-none font-mono text-sm"
                                />
                                <button
                                    onClick={() => setShowKeys({ ...showKeys, [config.key]: !showKeys[config.key] })}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-white"
                                >
                                    {showKeys[config.key] ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                </button>
                            </div>

                            {errors[config.key] && (
                                <div className="p-2 bg-red-500/10 border border-red-500/50 rounded text-red-400 text-xs flex items-center gap-2">
                                    <AlertCircle className="w-3 h-3" />
                                    {errors[config.key]}
                                </div>
                            )}

                            {success[config.key] && (
                                <div className="p-2 bg-green-500/10 border border-green-500/50 rounded text-green-400 text-xs flex items-center gap-2">
                                    <Check className="w-3 h-3" />
                                    {success[config.key]}
                                </div>
                            )}

                            <button
                                onClick={() => onValidate(config.key)}
                                disabled={validating[config.key] || !apiKeys[config.key]}
                                className="w-full py-2 bg-primary/20 hover:bg-primary/30 text-primary border border-primary/30 font-bold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                            >
                                {validating[config.key] ? 'Validating...' : hasKey ? 'Update Key' : 'Validate & Save Key'}
                            </button>
                        </div>
                    </div>
                );
            })}

            <div className="p-4 bg-blue-500/10 border border-blue-500/30 rounded-xl">
                <h4 className="font-bold text-blue-400 mb-2 text-sm flex items-center gap-2">
                    <Zap className="w-4 h-4" />
                    Free Option: Local Web LLM
                </h4>
                <p className="text-xs text-muted-foreground">
                    Don't want to use API keys? The built-in Local Web LLM generates summaries without any external services - completely free and private!
                </p>
            </div>
        </div>
    );
};

export default Settings;
