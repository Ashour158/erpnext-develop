# Voice Interface Module
# Voice commands, speech-to-text, and voice navigation

from .voice_commands import VoiceCommands
from .speech_to_text import SpeechToText
from .text_to_speech import TextToSpeech
from .voice_navigation import VoiceNavigation
from .voice_search import VoiceSearch
from .voice_reporting import VoiceReporting
from .voice_collaboration import VoiceCollaboration
from .voice_accessibility import VoiceAccessibility

__all__ = [
    'VoiceCommands',
    'SpeechToText',
    'TextToSpeech',
    'VoiceNavigation',
    'VoiceSearch',
    'VoiceReporting',
    'VoiceCollaboration',
    'VoiceAccessibility'
]
