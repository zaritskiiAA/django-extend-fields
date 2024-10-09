import os

from deepl.translator import Translator
from deepl.api_data import TextResult
from deepl.exceptions import ConnectionException
from pydantic import BaseModel, ValidationError

from .bases import TranslatorBase, ApiHandler
from .exceptions import TranslatorConnectionError, TranslatorDataError


class TextResultModel(BaseModel):

    text: str
    detected_source_lang: str


class DeeplTranslator(TranslatorBase, ApiHandler):

    LANGUAGE_MAPPER: dict[str, str] = {
        'en_us': 'EN-US',
        'ru': 'RU',
        'de': 'DE',
    }

    @classmethod
    def _get_language_mapper(cls):

        assert hasattr(cls, 'LANGUAGE_MAPPER'), (
            'Cls attr LANGUAGE_MAPPER must be set for mapping django '
            'language codes to deepl codes or override "_get_language_mapper" method.'
        )
        assert isinstance(cls.LANGUAGE_MAPPER, dict), 'Cls attr LANGUAGE_MAPPER must be dict.'
        assert all(
            isinstance(key, str) and isinstance(value, str)
            for key, value in cls.LANGUAGE_MAPPER.items()
        ), 'Type items in cls attr LANGUAGE_MAPPER must be str.'

        return cls.LANGUAGE_MAPPER

    def __init__(self, translator: Translator) -> None:

        self.translator = translator

    def validate_response(self, response: TextResult) -> TextResultModel:

        if not isinstance(response, TextResult):
            raise TranslatorDataError('Deepl response must be TextResult instance.')

        try:
            return TextResultModel(
                text=response.text,
                detected_source_lang=response.detected_source_lang,
            )
        except ValidationError as e:
            raise TranslatorDataError(
                f'Deepl response data cant parse to TextResultModel. Pudantic error: {str(e)}'
            )

    def make_request(self, *args, **kwargs) -> TextResult:
        try:
            response = self.translator.translate_text(*args, **kwargs)
        except ConnectionException as e:
            raise TranslatorConnectionError(
                f'DeeplTranslator request was failed with exception {e}: {e.args}',
            )
        return response

    def translate_text(self, src_text: str, target_lang: str) -> TextResultModel:

        deepl_lang_code = self._get_language_mapper().get(target_lang)

        if not deepl_lang_code:
            # TODO: сделать метод с re.
            target_lang = (
                target_lang.replace("_", "-")
                if "_" in target_lang
                else target_lang.replace("-", "_")  # noqa E501
            )
            if deepl_lang_code := self._get_language_mapper().get(target_lang):
                pass
            else:
                raise TranslatorDataError(
                    f'Target language does not exists in LANGUAGE_MAPPER. {deepl_lang_code}'
                )

        response = self.make_request(src_text, target_lang=deepl_lang_code)
        self.validate_response(response)
        return self.validate_response(response)


def get_translator():
    """Used it in your ExtendField parametrs if you need DeeplTranslator."""

    if key := os.getenv("DEEPL_TRANSLATOR_KEY"):

        from deepl import Translator

        deepl_translator = DeeplTranslator(Translator(key))
        return deepl_translator
    else:
        raise AttributeError('DEEPL_TRANSLATOR_KEY not found in env params.')
