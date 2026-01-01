import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Key, Settings as SettingsIcon, Check, AlertCircle, ChevronDown, Eye, EyeOff, Trash2 } from 'lucide-react';
import axios from 'axios';

const Settings = ({ isOpen, onClose }) => {
    const [settings, setSettings] = useState(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('providers');
    const [apiKeys, setApiKeys] = useState({});
    const [showKeys, setShowKeys] = useState({});
    const [validating, setValidating] = useState({});
    const [errors, setErrors] = useState({});
    const [success, setSuccess] = useState({});
    const [selectedProvider, setSelectedProvider] = useState('');
    const [selectedModel, setSelectedModel] = useState('');

    useEffect(() => {
        if (isOpen) {
            fetchSettings();
        }
    }, [isOpen]);

    const fetchSettings = async () => {
        try {
            setLoading(true);
            const response = await axios.get('http://localhost:8000/api/settings');
            setSettings(response.data);
            setSelectedProvider(response.data.llm_provider || 'cohere');
            setSelectedModel(response.data.llm_model || '');
        } catch (err) {
            console.error('Error fetching settings:', err);
            setErrors({ general: 'Failed to load settings' });
        } finally {
            setLoading(false);
        }
    };

    const handleSaveApiKey = async (provider) => {
        const apiKey = apiKeys[provider];
        if (!apiKey || !apiKey.trim()) {
            setErrors({ ...errors, [provider]: 'API key cannot be empty' });
            return;
        }

        setValidating({ ...validating, [provider]: true });
        setErrors({ ...errors, [provider]: null });
        setSuccess({ ...success, [provider]: null });

        try {
            const response = await axios.post('http://localhost:8000/api/settings/api-key', {
                provider,
                api_key: apiKey,
                validate: true
            });

            setSuccess({ ...success, [provider]: response.data.message });
            setApiKeys({ ...apiKeys, [provider]: '' });

            // Refresh settings
            await fetchSettings();
        } catch (err) {
            setErrors({
                ...errors,
                [provider]: err.response?.data?.detail || 'Failed to save API key'
            });
        } finally {
            setValidating({ ...validating, [provider]: false });
        }
    };

    const handleDeleteApiKey = async (provider) => {
        if (!confirm(`Are you sure you want to delete the ${provider} API key?`)) {
            return;
        }

        try {
            await axios.delete(`http://localhost:8000/api/settings/api-key/${provider}`);
            setSuccess({ ...success, [provider]: 'API key deleted successfully' });
            await fetchSettings();
        } catch (err) {
            setErrors({
                ...errors,
                [provider]: err.response?.data?.detail || 'Failed to delete API key'
            });
        }
    };

    const handleSwitchProvider = async () => {
        try {
            const response = await axios.post('http://localhost:8000/api/settings/provider', {
                provider: selectedProvider,
                model: selectedModel || null
            });

            setSuccess({ provider: response.data.message });
            await fetchSettings();
        } catch (err) {
            setErrors({
                provider: err.response?.data?.detail || 'Failed to switch provider'
            });
        }
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
                                <p className="text-sm text-muted-foreground">Manage API keys and LLM preferences</p>
                            </div>
                        </div>
                        <button
                            onClick={onClose}
                            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                        >
                            <X className="w-5 h-5 text-muted-foreground" />
                        </button>
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
                            LLM PROVIDERS
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
                    <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
                        {loading ? (
                            <div className="flex items-center justify-center py-12">
                                <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
                            </div>
                        ) : activeTab === 'providers' ? (
                            <ProvidersTab
                                settings={settings}
                                selectedProvider={selectedProvider}
                                setSelectedProvider={setSelectedProvider}
                                selectedModel={selectedModel}
                                setSelectedModel={setSelectedModel}
                                onSave={handleSwitchProvider}
                                error={errors.provider}
                                success={success.provider}
                            />
                        ) : (
                            <ApiKeysTab
                                settings={settings}
                                apiKeys={apiKeys}
                                setApiKeys={setApiKeys}
                                showKeys={showKeys}
                                setShowKeys={setShowKeys}
                                validating={validating}
                                errors={errors}
                                success={success}
                                onSave={handleSaveApiKey}
                                onDelete={handleDeleteApiKey}
                            />
                        )}
                    </div>
                </motion.div>
            </motion.div>
        </AnimatePresence>
    );
};

const ProvidersTab = ({ settings, selectedProvider, setSelectedProvider, selectedModel, setSelectedModel, onSave, error, success }) => {
    const providers = settings?.available_providers || {};
    const models = settings?.models || {};

    return (
        <div className="space-y-6">
            <div>
                <h3 className="text-lg font-bold text-white mb-4">Active LLM Provider</h3>
                <p className="text-sm text-muted-foreground mb-6">
                    Choose which AI model to use for generating summaries and insights
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {Object.entries(providers).map(([key, provider]) => (
                        <motion.button
                            key={key}
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            onClick={() => {
                                setSelectedProvider(key);
                                // Set default recommended model
                                const defaultModel = models[key]?.find(m => m.recommended)?.id || models[key]?.[0]?.id || '';
                                setSelectedModel(defaultModel);
                            }}
                            disabled={!provider.enabled && key !== 'local_wasm'}
                            className={`p-4 rounded-xl border text-left transition-all ${
                                selectedProvider === key
                                    ? 'border-primary bg-primary/10'
                                    : provider.enabled || key === 'local_wasm'
                                    ? 'border-white/10 hover:border-white/20 bg-white/5'
                                    : 'border-white/5 bg-white/5 opacity-50 cursor-not-allowed'
                            }`}
                        >
                            <div className="flex items-start justify-between mb-2">
                                <h4 className="font-bold text-white">{provider.name}</h4>
                                {selectedProvider === key && (
                                    <Check className="w-5 h-5 text-primary" />
                                )}
                            </div>
                            <p className="text-xs text-muted-foreground mb-2">{provider.description}</p>
                            <div className="flex items-center gap-2">
                                <span className={`text-xs px-2 py-1 rounded ${
                                    provider.enabled || key === 'local_wasm'
                                        ? 'bg-green-500/20 text-green-400'
                                        : 'bg-red-500/20 text-red-400'
                                }`}>
                                    {provider.enabled || key === 'local_wasm' ? 'READY' : 'NO API KEY'}
                                </span>
                            </div>
                        </motion.button>
                    ))}
                </div>
            </div>

            {selectedProvider && models[selectedProvider] && models[selectedProvider].length > 0 && (
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

const ApiKeysTab = ({ settings, apiKeys, setApiKeys, showKeys, setShowKeys, validating, errors, success, onSave, onDelete }) => {
    const providers = settings?.available_providers || {};

    const providerConfigs = [
        { key: 'anthropic', name: 'Anthropic Claude', placeholder: 'sk-ant-...' },
        { key: 'cohere', name: 'Cohere', placeholder: 'your-cohere-api-key' },
        { key: 'groq', name: 'Groq', placeholder: 'gsk_...' },
    ];

    return (
        <div className="space-y-6">
            <div>
                <h3 className="text-lg font-bold text-white mb-2">API Key Management</h3>
                <p className="text-sm text-muted-foreground mb-6">
                    Add and manage your API keys for different LLM providers. Keys are stored securely in your .env file.
                </p>
            </div>

            {providerConfigs.map((provider) => {
                const hasKey = providers[provider.key]?.enabled;

                return (
                    <div key={provider.key} className="p-4 bg-white/5 rounded-xl border border-white/10">
                        <div className="flex items-start justify-between mb-3">
                            <div>
                                <h4 className="font-bold text-white flex items-center gap-2">
                                    <Key className="w-4 h-4 text-primary" />
                                    {provider.name}
                                </h4>
                                <p className="text-xs text-muted-foreground mt-1">
                                    {hasKey ? 'API key configured' : 'No API key configured'}
                                </p>
                            </div>
                            {hasKey && (
                                <button
                                    onClick={() => onDelete(provider.key)}
                                    className="p-2 hover:bg-red-500/20 rounded-lg transition-colors group"
                                    title="Delete API key"
                                >
                                    <Trash2 className="w-4 h-4 text-muted-foreground group-hover:text-red-400" />
                                </button>
                            )}
                        </div>

                        <div className="space-y-3">
                            <div className="relative">
                                <input
                                    type={showKeys[provider.key] ? 'text' : 'password'}
                                    value={apiKeys[provider.key] || ''}
                                    onChange={(e) => setApiKeys({ ...apiKeys, [provider.key]: e.target.value })}
                                    placeholder={provider.placeholder}
                                    className="w-full px-4 py-3 pr-10 bg-black/30 border border-white/10 rounded-lg text-white placeholder-muted-foreground focus:border-primary focus:outline-none font-mono text-sm"
                                />
                                <button
                                    onClick={() => setShowKeys({ ...showKeys, [provider.key]: !showKeys[provider.key] })}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-white"
                                >
                                    {showKeys[provider.key] ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                </button>
                            </div>

                            {errors[provider.key] && (
                                <div className="p-2 bg-red-500/10 border border-red-500/50 rounded text-red-400 text-xs flex items-center gap-2">
                                    <AlertCircle className="w-3 h-3" />
                                    {errors[provider.key]}
                                </div>
                            )}

                            {success[provider.key] && (
                                <div className="p-2 bg-green-500/10 border border-green-500/50 rounded text-green-400 text-xs flex items-center gap-2">
                                    <Check className="w-3 h-3" />
                                    {success[provider.key]}
                                </div>
                            )}

                            <button
                                onClick={() => onSave(provider.key)}
                                disabled={validating[provider.key]}
                                className="w-full py-2 bg-primary/20 hover:bg-primary/30 text-primary border border-primary/30 font-bold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                            >
                                {validating[provider.key] ? 'Validating...' : 'Save & Validate Key'}
                            </button>
                        </div>
                    </div>
                );
            })}

            <div className="p-4 bg-blue-500/10 border border-blue-500/30 rounded-xl">
                <h4 className="font-bold text-blue-400 mb-2 text-sm">Local WASM Models (Coming Soon)</h4>
                <p className="text-xs text-muted-foreground">
                    Run AI models entirely in your browser with WebAssembly - no API keys required, complete privacy.
                </p>
            </div>
        </div>
    );
};

export default Settings;
