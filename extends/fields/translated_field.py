import re
from typing import Callable, Any

from django.utils.translation import get_language
from django.db.models import Model
from django.db.models.fields import Field
from django.conf import settings

from extends.bases import ExtendFieldDescriptor, ExtendModelOptions, ConverterMixin


def to_attribute(name, language_code=None):
    language = language_code or get_language()
    return re.sub(r"[^a-z0-9_]+", "_", (f"{name}_{language}").lower())


def translated_attrgetter(name, field):
    return lambda self: getattr(self, to_attribute(name, get_language() or field.attr_suffix[0]))


def translated_attrsetter(name, field):

    def _setter(self, value):

        for v in field.validators:
            v.validate(value)

        if hasattr(field, '_auto'):
            for suf in field.auto.suffix:
                convert_value = field.auto.converter.translate_text(value, suf).text
                setattr(self, to_attribute(name, suf), convert_value)
        else:
            setattr(self, to_attribute(name), value)

    return _setter


def _to_orm(desc_kwargs: dict[str, str], orm_call: Callable[..., Any], *args, **kwargs) -> Any:

    for desc, raw_data in desc_kwargs.items():
        convert_kwargs = raw_data.copy()
        for raw_field, value in raw_data.items():
            if hasattr(desc, '_auto'):
                suf = raw_field.replace(f'{desc.attrname}_', "")
                convert_kwargs[raw_field] = desc.auto.converter.translate_text(value, suf).text
        kwargs.update(convert_kwargs)
    return orm_call(*args, **kwargs)


class TranslatedField(ExtendFieldDescriptor, ConverterMixin):

    def __init__(
        self,
        field: Field,
        specific=None,
        *,
        attr_suffix=None,
        attrgetter=translated_attrgetter,
        attrsetter=translated_attrsetter,
        auto=None,
        validators=None,
    ) -> None:

        attr_suffix = list(attr_suffix or (lang[0] for lang in settings.LANGUAGES))

        super().__init__(
            field,
            specific,
            attr_suffix=attr_suffix,
            attrgetter=attrgetter,
            attrsetter=attrsetter,
            validators=validators,
        )
        if auto:
            self._create_auto_property(auto)

    def _create_auto_property(self, converter_data) -> None:

        conv = converter_data[0]() if converter_data[0] else None
        suffix = converter_data[1] or self.attr_suffix
        super()._create_auto_property((conv, suffix))

    def to_attribute(self, name: str, suffix: str | None = None) -> str:
        return to_attribute(name, language_code=suffix)

    def contribute_to_class(self, model_cls: Model, name: str) -> None:
        super().contribute_to_class(model_cls, name)
        ExtendModelOptions.install(model_cls, name, self, orm_proxy=_to_orm)
