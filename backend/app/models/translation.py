"""
Translation models and type definitions.

This module defines the core types and metadata for the multilingual translation feature.
"""

from typing import Literal, TypedDict
from pydantic import BaseModel, Field, computed_field


# SupportedLanguage type - defines all languages supported by the translation system
SupportedLanguage = Literal[
    "english",
    "urdu",
    "mandarin",
    "japanese",
    "spanish",
    "french",
    "arabic",
]


class LanguageMetadata(TypedDict):
    """Type definition for language metadata entries."""

    name: str
    native_name: str
    rtl: bool


# Language metadata dictionary with display names, native names, and RTL flags
LANGUAGE_METADATA: dict[SupportedLanguage, LanguageMetadata] = {
    "english": {
        "name": "English",
        "native_name": "English",
        "rtl": False,
    },
    "urdu": {
        "name": "Urdu",
        "native_name": "اردو",
        "rtl": True,
    },
    "mandarin": {
        "name": "Mandarin Chinese",
        "native_name": "中文",
        "rtl": False,
    },
    "japanese": {
        "name": "Japanese",
        "native_name": "日本語",
        "rtl": False,
    },
    "spanish": {
        "name": "Spanish",
        "native_name": "Español",
        "rtl": False,
    },
    "french": {
        "name": "French",
        "native_name": "Français",
        "rtl": False,
    },
    "arabic": {
        "name": "Arabic",
        "native_name": "العربية",
        "rtl": True,
    },
}


class TranslateTextResponse(BaseModel):
    """Response model for text translation endpoint.

    This model represents the result of translating text from one language to another.
    The RTL (right-to-left) flag is automatically derived from the target language's
    metadata to support proper text rendering in the frontend.

    The rtl field is a computed field that looks up the RTL property from LANGUAGE_METADATA
    based on the target_language. This ensures consistency and eliminates the possibility
    of mismatched RTL flags.

    Example:
        >>> response = TranslateTextResponse(
        ...     original_text="Hello world",
        ...     translated_text="Hola mundo",
        ...     source_language="english",
        ...     target_language="spanish"
        ... )
        >>> response.rtl
        False
        >>> response.target_language
        'spanish'

    Example with RTL language:
        >>> response = TranslateTextResponse(
        ...     original_text="Hello",
        ...     translated_text="مرحبا",
        ...     source_language="english",
        ...     target_language="arabic"
        ... )
        >>> response.rtl
        True

    Attributes:
        original_text: The original text before translation (non-empty, 1+ chars)
        translated_text: The translated text (non-empty, 1+ chars)
        source_language: Source language of the original text
        target_language: Target language for the translation
        rtl: Right-to-left flag, automatically derived from target_language metadata
    """

    original_text: str = Field(
        ...,
        min_length=1,
        description="Original text before translation"
    )

    translated_text: str = Field(
        ...,
        min_length=1,
        description="Translated text"
    )

    source_language: SupportedLanguage = Field(
        ...,
        description="Source language of the original text"
    )

    target_language: SupportedLanguage = Field(
        ...,
        description="Target language for the translation"
    )

    @computed_field
    @property
    def rtl(self) -> bool:
        """Automatically derive RTL flag from target language metadata.

        Returns:
            bool: True if target language is RTL (Arabic, Urdu), False otherwise
        """
        return LANGUAGE_METADATA[self.target_language]["rtl"]
