"""Settings manager for API keys and LLM configuration"""

import os
import json
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv, set_key, find_dotenv

class SettingsManager:
    """Manage application settings including API keys and LLM preferences"""

    def __init__(self):
        self.env_file = find_dotenv() or '.env'
        self.settings_file = Path('.settings.json')
        load_dotenv(self.env_file)

    def get_settings(self) -> Dict:
        """Get all current settings"""
        settings = {
            'llm_provider': os.getenv('LLM_PROVIDER', 'cohere'),
            'llm_model': os.getenv('LLM_MODEL', ''),
            'api_keys': {
                'anthropic': bool(os.getenv('ANTHROPIC_API_KEY')),
                'cohere': bool(os.getenv('COHERE_API_KEY')),
                'groq': bool(os.getenv('GROQ_API_KEY')),
            },
            'available_providers': self._get_available_providers(),
            'models': self._get_available_models()
        }

        # Load additional settings from JSON file
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    extra_settings = json.load(f)
                    settings.update(extra_settings)
            except Exception:
                pass

        return settings

    def _get_available_providers(self) -> Dict[str, Dict]:
        """Get list of available LLM providers with their status"""
        return {
            'anthropic': {
                'name': 'Anthropic Claude',
                'enabled': bool(os.getenv('ANTHROPIC_API_KEY')),
                'description': 'High-quality AI summaries with Claude Sonnet 4.5'
            },
            'cohere': {
                'name': 'Cohere',
                'enabled': bool(os.getenv('COHERE_API_KEY')),
                'description': 'Fast and accurate with Command-A models'
            },
            'groq': {
                'name': 'Groq',
                'enabled': bool(os.getenv('GROQ_API_KEY')),
                'description': 'Ultra-fast inference with LPU technology'
            },
            'local_wasm': {
                'name': 'Local WASM (Browser)',
                'enabled': True,  # Always available
                'description': 'Privacy-focused, runs entirely in your browser (coming soon)'
            }
        }

    def _get_available_models(self) -> Dict[str, list]:
        """Get available models for each provider"""
        return {
            'anthropic': [
                {'id': 'claude-sonnet-4-20250514', 'name': 'Claude Sonnet 4.5', 'recommended': True},
                {'id': 'claude-opus-4-20250514', 'name': 'Claude Opus 4', 'recommended': False},
                {'id': 'claude-3-5-sonnet-20241022', 'name': 'Claude 3.5 Sonnet', 'recommended': False}
            ],
            'cohere': [
                {'id': 'command-a-03-2025', 'name': 'Command-A (March 2025)', 'recommended': True},
                {'id': 'command-r-plus', 'name': 'Command R+', 'recommended': False},
                {'id': 'command-r', 'name': 'Command R', 'recommended': False}
            ],
            'groq': [
                {'id': 'llama-3.3-70b-versatile', 'name': 'Llama 3.3 70B', 'recommended': True},
                {'id': 'llama-3.1-70b-versatile', 'name': 'Llama 3.1 70B', 'recommended': False},
                {'id': 'mixtral-8x7b-32768', 'name': 'Mixtral 8x7B', 'recommended': False}
            ],
            'local_wasm': [
                {'id': 'phi-3-mini', 'name': 'Phi-3 Mini (3.8B)', 'recommended': True},
                {'id': 'gemma-2b', 'name': 'Gemma 2B', 'recommended': False}
            ]
        }

    def validate_api_key(self, provider: str, api_key: str) -> Dict:
        """
        Validate an API key by making a test request

        Returns:
            Dict with 'valid' (bool) and 'message' (str)
        """
        if not api_key or not api_key.strip():
            return {'valid': False, 'message': 'API key cannot be empty'}

        try:
            if provider == 'anthropic':
                import anthropic
                client = anthropic.Anthropic(api_key=api_key)
                # Test with a minimal request
                client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=10,
                    messages=[{"role": "user", "content": "Hi"}]
                )
                return {'valid': True, 'message': 'API key validated successfully'}

            elif provider == 'cohere':
                import cohere
                client = cohere.ClientV2(api_key=api_key)
                # Test with a minimal request
                client.chat(
                    model="command-a-03-2025",
                    messages=[{"role": "user", "content": "Hi"}],
                    max_tokens=10
                )
                return {'valid': True, 'message': 'API key validated successfully'}

            elif provider == 'groq':
                from groq import Groq
                client = Groq(api_key=api_key)
                # Test with a minimal request
                client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": "Hi"}],
                    max_tokens=10
                )
                return {'valid': True, 'message': 'API key validated successfully'}

            else:
                return {'valid': False, 'message': f'Unknown provider: {provider}'}

        except Exception as e:
            error_msg = str(e)
            if '401' in error_msg or 'unauthorized' in error_msg.lower():
                return {'valid': False, 'message': 'Invalid API key'}
            elif '429' in error_msg or 'rate limit' in error_msg.lower():
                return {'valid': True, 'message': 'API key valid (rate limited but authenticated)'}
            else:
                return {'valid': False, 'message': f'Validation error: {error_msg[:100]}'}

    def save_api_key(self, provider: str, api_key: str, validate: bool = True) -> Dict:
        """
        Save an API key to the .env file

        Args:
            provider: Provider name (anthropic, cohere, groq)
            api_key: The API key to save
            validate: Whether to validate the key before saving

        Returns:
            Dict with 'success' (bool) and 'message' (str)
        """
        if validate:
            validation = self.validate_api_key(provider, api_key)
            if not validation['valid']:
                return {'success': False, 'message': validation['message']}

        # Map provider to env var name
        env_var_map = {
            'anthropic': 'ANTHROPIC_API_KEY',
            'cohere': 'COHERE_API_KEY',
            'groq': 'GROQ_API_KEY'
        }

        if provider not in env_var_map:
            return {'success': False, 'message': f'Unknown provider: {provider}'}

        env_var = env_var_map[provider]

        try:
            # Create .env file if it doesn't exist
            if not os.path.exists(self.env_file):
                Path(self.env_file).touch()

            # Update the .env file
            set_key(self.env_file, env_var, api_key)

            # Reload environment variables
            load_dotenv(self.env_file, override=True)

            return {'success': True, 'message': f'{provider.title()} API key saved successfully'}

        except Exception as e:
            return {'success': False, 'message': f'Error saving API key: {str(e)}'}

    def update_provider(self, provider: str, model: Optional[str] = None) -> Dict:
        """
        Update the active LLM provider and optionally the model

        Args:
            provider: Provider name (anthropic, cohere, groq, local_wasm)
            model: Optional model ID

        Returns:
            Dict with 'success' (bool) and 'message' (str)
        """
        valid_providers = ['anthropic', 'cohere', 'groq', 'local_wasm']

        if provider not in valid_providers:
            return {'success': False, 'message': f'Invalid provider. Must be one of: {valid_providers}'}

        # Check if provider has an API key (except for local_wasm)
        if provider != 'local_wasm':
            env_var_map = {
                'anthropic': 'ANTHROPIC_API_KEY',
                'cohere': 'COHERE_API_KEY',
                'groq': 'GROQ_API_KEY'
            }
            if not os.getenv(env_var_map[provider]):
                return {'success': False, 'message': f'No API key found for {provider}. Please add one first.'}

        try:
            # Create .env file if it doesn't exist
            if not os.path.exists(self.env_file):
                Path(self.env_file).touch()

            # Update provider
            set_key(self.env_file, 'LLM_PROVIDER', provider)

            # Update model if provided
            if model:
                set_key(self.env_file, 'LLM_MODEL', model)

            # Reload environment variables
            load_dotenv(self.env_file, override=True)

            return {'success': True, 'message': f'Switched to {provider}' + (f' ({model})' if model else '')}

        except Exception as e:
            return {'success': False, 'message': f'Error updating provider: {str(e)}'}

    def delete_api_key(self, provider: str) -> Dict:
        """
        Delete an API key from the .env file

        Args:
            provider: Provider name (anthropic, cohere, groq)

        Returns:
            Dict with 'success' (bool) and 'message' (str)
        """
        env_var_map = {
            'anthropic': 'ANTHROPIC_API_KEY',
            'cohere': 'COHERE_API_KEY',
            'groq': 'GROQ_API_KEY'
        }

        if provider not in env_var_map:
            return {'success': False, 'message': f'Unknown provider: {provider}'}

        env_var = env_var_map[provider]

        try:
            # Remove from .env file by setting empty value
            set_key(self.env_file, env_var, '')

            # Reload environment variables
            load_dotenv(self.env_file, override=True)

            return {'success': True, 'message': f'{provider.title()} API key deleted'}

        except Exception as e:
            return {'success': False, 'message': f'Error deleting API key: {str(e)}'}
