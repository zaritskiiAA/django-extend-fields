from typing import Any
from abc import ABC, abstractmethod

from pydantic import BaseModel


class TranslatorBase(ABC):

    @abstractmethod
    def translate_text(self, src_text: str, target_lang: str) -> BaseModel:
        pass


class LanguageDetectorBase(ABC):

    @abstractmethod
    def detect_languages(self, text: str) -> BaseModel:
        pass


class ApiHandler(ABC):

    @abstractmethod
    def validate_response(self, response: Any) -> BaseModel:
        pass

    @abstractmethod
    def make_request(self, *args, **kwargs) -> Any:
        pass
