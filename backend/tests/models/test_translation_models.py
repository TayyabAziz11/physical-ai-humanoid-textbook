"""
Tests for translation models.

Task 1.1: Test SupportedLanguage type definition and validation.
Task 1.2: Test TranslateTextRequest model and validation.
"""

import pytest
from typing import get_args
from pydantic import BaseModel, ValidationError

from app.models.translation import SupportedLanguage, LANGUAGE_METADATA
from app.models.request import TranslateTextRequest


class TestSupportedLanguageType:
    """Test suite for SupportedLanguage Literal type."""

    def test_supported_language_has_seven_values(self):
        """Test that SupportedLanguage includes all 7 supported languages."""
        languages = get_args(SupportedLanguage)
        assert len(languages) == 7, f"Expected 7 languages, got {len(languages)}"

    def test_supported_language_includes_required_languages(self):
        """Test that all required languages are in SupportedLanguage."""
        languages = get_args(SupportedLanguage)
        required = {"english", "urdu", "mandarin", "japanese", "spanish", "french", "arabic"}
        assert set(languages) == required, f"Language mismatch: {set(languages)} vs {required}"

    def test_unsupported_language_not_in_type(self):
        """Test that unsupported languages are not in SupportedLanguage."""
        languages = get_args(SupportedLanguage)
        assert "german" not in languages
        assert "russian" not in languages
        assert "korean" not in languages

    def test_empty_string_not_supported(self):
        """Test that empty string is not a valid language."""
        languages = get_args(SupportedLanguage)
        assert "" not in languages

    def test_pydantic_validation_accepts_valid_language(self):
        """Test that Pydantic accepts valid SupportedLanguage values."""

        class TestModel(BaseModel):
            language: SupportedLanguage

        # Test each valid language
        for lang in ["english", "urdu", "mandarin", "japanese", "spanish", "french", "arabic"]:
            model = TestModel(language=lang)
            assert model.language == lang

    def test_pydantic_validation_rejects_invalid_language(self):
        """Test that Pydantic rejects invalid language values."""

        class TestModel(BaseModel):
            language: SupportedLanguage

        # Test invalid languages
        with pytest.raises(ValidationError) as exc_info:
            TestModel(language="german")
        assert "Input should be 'english'" in str(exc_info.value) or "literal_error" in str(exc_info.value)

        with pytest.raises(ValidationError):
            TestModel(language="")

        with pytest.raises(ValidationError):
            TestModel(language="ENGLISH")  # Case sensitive


class TestLanguageMetadata:
    """Test suite for LANGUAGE_METADATA dictionary."""

    def test_language_metadata_exists(self):
        """Test that LANGUAGE_METADATA is defined."""
        assert LANGUAGE_METADATA is not None
        assert isinstance(LANGUAGE_METADATA, dict)

    def test_language_metadata_has_all_languages(self):
        """Test that LANGUAGE_METADATA contains all supported languages."""
        languages = get_args(SupportedLanguage)
        for lang in languages:
            assert lang in LANGUAGE_METADATA, f"{lang} missing from LANGUAGE_METADATA"

    def test_language_metadata_has_required_fields(self):
        """Test that each language metadata has required fields."""
        required_fields = {"name", "native_name", "rtl"}

        for lang, metadata in LANGUAGE_METADATA.items():
            assert isinstance(metadata, dict), f"{lang} metadata should be a dict"
            for field in required_fields:
                assert field in metadata, f"{lang} missing field: {field}"

    def test_rtl_languages_flagged_correctly(self):
        """Test that RTL languages (Arabic, Urdu) are flagged as RTL."""
        assert LANGUAGE_METADATA["arabic"]["rtl"] is True
        assert LANGUAGE_METADATA["urdu"]["rtl"] is True

    def test_ltr_languages_flagged_correctly(self):
        """Test that LTR languages are flagged as not RTL."""
        ltr_languages = ["english", "spanish", "french", "mandarin", "japanese"]
        for lang in ltr_languages:
            assert LANGUAGE_METADATA[lang]["rtl"] is False

    def test_language_metadata_has_native_names(self):
        """Test that language metadata includes native names."""
        assert LANGUAGE_METADATA["spanish"]["native_name"] == "Español"
        assert LANGUAGE_METADATA["french"]["native_name"] == "Français"
        assert LANGUAGE_METADATA["arabic"]["native_name"] == "العربية"
        assert LANGUAGE_METADATA["urdu"]["native_name"] == "اردو"
        assert LANGUAGE_METADATA["mandarin"]["native_name"] == "中文"
        assert LANGUAGE_METADATA["japanese"]["native_name"] == "日本語"
        assert LANGUAGE_METADATA["english"]["native_name"] == "English"


class TestTranslateTextRequest:
    """Test suite for TranslateTextRequest Pydantic model."""

    def test_create_valid_request_with_minimal_fields(self):
        """Test creating a valid request with only required fields."""
        request = TranslateTextRequest(
            text="Hello world",
            target_language="spanish"
        )
        assert request.text == "Hello world"
        assert request.target_language == "spanish"
        assert request.source_language == "english"  # Default value
        assert request.preserve_technical_terms is True  # Default value
        assert request.context is None  # Default value

    def test_create_valid_request_with_all_fields(self):
        """Test creating a valid request with all fields specified."""
        request = TranslateTextRequest(
            text="ROS 2 is a robotics framework",
            target_language="urdu",
            source_language="english",
            preserve_technical_terms=False,
            context="robotics documentation"
        )
        assert request.text == "ROS 2 is a robotics framework"
        assert request.target_language == "urdu"
        assert request.source_language == "english"
        assert request.preserve_technical_terms is False
        assert request.context == "robotics documentation"

    def test_default_source_language_is_english(self):
        """Test that source_language defaults to 'english'."""
        request = TranslateTextRequest(text="Test", target_language="french")
        assert request.source_language == "english"

    def test_default_preserve_technical_terms_is_true(self):
        """Test that preserve_technical_terms defaults to True."""
        request = TranslateTextRequest(text="Test", target_language="spanish")
        assert request.preserve_technical_terms is True

    def test_text_min_length_validation(self):
        """Test that empty text is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TranslateTextRequest(text="", target_language="spanish")
        assert "String should have at least 1 character" in str(exc_info.value) or "at least 1 character" in str(exc_info.value).lower()

    def test_text_max_length_validation(self):
        """Test that text exceeding 10000 characters is rejected."""
        long_text = "x" * 10001
        with pytest.raises(ValidationError) as exc_info:
            TranslateTextRequest(text=long_text, target_language="spanish")
        assert "String should have at most 10000 characters" in str(exc_info.value) or "at most 10000 character" in str(exc_info.value).lower()

    def test_text_exactly_10000_characters_is_valid(self):
        """Test that text with exactly 10000 characters is accepted."""
        text = "x" * 10000
        request = TranslateTextRequest(text=text, target_language="spanish")
        assert len(request.text) == 10000

    def test_invalid_target_language_rejected(self):
        """Test that invalid target language is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TranslateTextRequest(text="Hello", target_language="german")
        error_str = str(exc_info.value).lower()
        assert "input should be" in error_str or "literal_error" in error_str

    def test_invalid_source_language_rejected(self):
        """Test that invalid source language is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TranslateTextRequest(
                text="Hello",
                target_language="spanish",
                source_language="russian"
            )
        error_str = str(exc_info.value).lower()
        assert "input should be" in error_str or "literal_error" in error_str

    def test_context_max_length_validation(self):
        """Test that context exceeding 200 characters is rejected."""
        long_context = "x" * 201
        with pytest.raises(ValidationError) as exc_info:
            TranslateTextRequest(
                text="Hello",
                target_language="spanish",
                context=long_context
            )
        assert "String should have at most 200 characters" in str(exc_info.value) or "at most 200 character" in str(exc_info.value).lower()

    def test_context_exactly_200_characters_is_valid(self):
        """Test that context with exactly 200 characters is accepted."""
        context = "x" * 200
        request = TranslateTextRequest(
            text="Hello",
            target_language="spanish",
            context=context
        )
        assert len(request.context) == 200

    def test_same_source_and_target_language_allowed(self):
        """Test that source and target can be the same language."""
        request = TranslateTextRequest(
            text="Hello",
            target_language="english",
            source_language="english"
        )
        assert request.source_language == "english"
        assert request.target_language == "english"

    def test_all_supported_languages_as_target(self):
        """Test that all supported languages work as target_language."""
        for lang in ["english", "urdu", "mandarin", "japanese", "spanish", "french", "arabic"]:
            request = TranslateTextRequest(text="Test", target_language=lang)
            assert request.target_language == lang

    def test_all_supported_languages_as_source(self):
        """Test that all supported languages work as source_language."""
        for lang in ["english", "urdu", "mandarin", "japanese", "spanish", "french", "arabic"]:
            request = TranslateTextRequest(
                text="Test",
                target_language="english",
                source_language=lang
            )
            assert request.source_language == lang

    def test_preserve_technical_terms_boolean_validation(self):
        """Test that preserve_technical_terms accepts boolean values."""
        request_true = TranslateTextRequest(
            text="Test",
            target_language="spanish",
            preserve_technical_terms=True
        )
        assert request_true.preserve_technical_terms is True

        request_false = TranslateTextRequest(
            text="Test",
            target_language="spanish",
            preserve_technical_terms=False
        )
        assert request_false.preserve_technical_terms is False

    def test_model_serialization(self):
        """Test that the model can be serialized to dict/JSON."""
        request = TranslateTextRequest(
            text="Hello world",
            target_language="spanish",
            preserve_technical_terms=True,
            context="test context"
        )
        data = request.model_dump()
        assert data["text"] == "Hello world"
        assert data["target_language"] == "spanish"
        assert data["source_language"] == "english"
        assert data["preserve_technical_terms"] is True
        assert data["context"] == "test context"

    def test_model_deserialization(self):
        """Test that the model can be created from dict."""
        data = {
            "text": "Bonjour",
            "target_language": "french",
            "source_language": "english",
            "preserve_technical_terms": False
        }
        request = TranslateTextRequest(**data)
        assert request.text == "Bonjour"
        assert request.target_language == "french"
        assert request.preserve_technical_terms is False


class TestTranslateTextResponse:
    """Test suite for TranslateTextResponse Pydantic model."""

    def test_create_valid_response_with_all_fields(self):
        """Test creating a valid response with all required fields."""
        from app.models.translation import TranslateTextResponse

        response = TranslateTextResponse(
            original_text="Hello world",
            translated_text="Hola mundo",
            source_language="english",
            target_language="spanish"
        )
        assert response.original_text == "Hello world"
        assert response.translated_text == "Hola mundo"
        assert response.source_language == "english"
        assert response.target_language == "spanish"
        assert response.rtl is False  # Spanish is LTR

    def test_rtl_flag_for_arabic_target(self):
        """Test that RTL flag is True for Arabic target language."""
        from app.models.translation import TranslateTextResponse

        response = TranslateTextResponse(
            original_text="Hello",
            translated_text="مرحبا",
            source_language="english",
            target_language="arabic"
        )
        assert response.rtl is True

    def test_rtl_flag_for_urdu_target(self):
        """Test that RTL flag is True for Urdu target language."""
        from app.models.translation import TranslateTextResponse

        response = TranslateTextResponse(
            original_text="Hello",
            translated_text="ہیلو",
            source_language="english",
            target_language="urdu"
        )
        assert response.rtl is True

    def test_rtl_flag_for_ltr_languages(self):
        """Test that RTL flag is False for LTR languages."""
        from app.models.translation import TranslateTextResponse

        ltr_languages = ["english", "spanish", "french", "mandarin", "japanese"]
        for lang in ltr_languages:
            response = TranslateTextResponse(
                original_text="Test",
                translated_text="Test translation",
                source_language="english",
                target_language=lang
            )
            assert response.rtl is False, f"{lang} should have rtl=False"

    def test_original_text_cannot_be_empty(self):
        """Test that empty original_text is rejected."""
        from app.models.translation import TranslateTextResponse

        with pytest.raises(ValidationError) as exc_info:
            TranslateTextResponse(
                original_text="",
                translated_text="Hola",
                source_language="english",
                target_language="spanish"
            )
        assert "String should have at least 1 character" in str(exc_info.value) or "at least 1 character" in str(exc_info.value).lower()

    def test_translated_text_cannot_be_empty(self):
        """Test that empty translated_text is rejected."""
        from app.models.translation import TranslateTextResponse

        with pytest.raises(ValidationError) as exc_info:
            TranslateTextResponse(
                original_text="Hello",
                translated_text="",
                source_language="english",
                target_language="spanish"
            )
        assert "String should have at least 1 character" in str(exc_info.value) or "at least 1 character" in str(exc_info.value).lower()

    def test_invalid_source_language_rejected(self):
        """Test that invalid source language is rejected."""
        from app.models.translation import TranslateTextResponse

        with pytest.raises(ValidationError) as exc_info:
            TranslateTextResponse(
                original_text="Hello",
                translated_text="Hola",
                source_language="german",
                target_language="spanish"
            )
        error_str = str(exc_info.value).lower()
        assert "input should be" in error_str or "literal_error" in error_str

    def test_invalid_target_language_rejected(self):
        """Test that invalid target language is rejected."""
        from app.models.translation import TranslateTextResponse

        with pytest.raises(ValidationError) as exc_info:
            TranslateTextResponse(
                original_text="Hello",
                translated_text="Hola",
                source_language="english",
                target_language="german"
            )
        error_str = str(exc_info.value).lower()
        assert "input should be" in error_str or "literal_error" in error_str

    def test_all_supported_languages_as_source(self):
        """Test that all supported languages work as source_language."""
        from app.models.translation import TranslateTextResponse

        for lang in ["english", "urdu", "mandarin", "japanese", "spanish", "french", "arabic"]:
            response = TranslateTextResponse(
                original_text="Test",
                translated_text="Translation",
                source_language=lang,
                target_language="english"
            )
            assert response.source_language == lang

    def test_all_supported_languages_as_target(self):
        """Test that all supported languages work as target_language."""
        from app.models.translation import TranslateTextResponse

        for lang in ["english", "urdu", "mandarin", "japanese", "spanish", "french", "arabic"]:
            response = TranslateTextResponse(
                original_text="Test",
                translated_text="Translation",
                source_language="english",
                target_language=lang
            )
            assert response.target_language == lang

    def test_same_source_and_target_language_allowed(self):
        """Test that source and target can be the same language."""
        from app.models.translation import TranslateTextResponse

        response = TranslateTextResponse(
            original_text="Hello",
            translated_text="Hello",
            source_language="english",
            target_language="english"
        )
        assert response.source_language == "english"
        assert response.target_language == "english"
        assert response.rtl is False

    def test_model_serialization(self):
        """Test that the model can be serialized to dict/JSON."""
        from app.models.translation import TranslateTextResponse

        response = TranslateTextResponse(
            original_text="Hello world",
            translated_text="Hola mundo",
            source_language="english",
            target_language="spanish"
        )
        data = response.model_dump()
        assert data["original_text"] == "Hello world"
        assert data["translated_text"] == "Hola mundo"
        assert data["source_language"] == "english"
        assert data["target_language"] == "spanish"
        assert data["rtl"] is False

    def test_model_deserialization(self):
        """Test that the model can be created from dict."""
        from app.models.translation import TranslateTextResponse

        data = {
            "original_text": "Bonjour",
            "translated_text": "Hello",
            "source_language": "french",
            "target_language": "english"
        }
        response = TranslateTextResponse(**data)
        assert response.original_text == "Bonjour"
        assert response.translated_text == "Hello"
        assert response.source_language == "french"
        assert response.target_language == "english"
        assert response.rtl is False

    def test_rtl_derived_from_language_metadata(self):
        """Test that RTL flag is correctly derived from LANGUAGE_METADATA."""
        from app.models.translation import TranslateTextResponse

        # Test RTL languages
        rtl_response = TranslateTextResponse(
            original_text="Test",
            translated_text="Test",
            source_language="english",
            target_language="arabic"
        )
        assert rtl_response.rtl is True
        assert LANGUAGE_METADATA["arabic"]["rtl"] is True

        # Test LTR languages
        ltr_response = TranslateTextResponse(
            original_text="Test",
            translated_text="Test",
            source_language="english",
            target_language="english"
        )
        assert ltr_response.rtl is False
        assert LANGUAGE_METADATA["english"]["rtl"] is False
