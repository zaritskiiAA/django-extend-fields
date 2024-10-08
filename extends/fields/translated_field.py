import re
from typing import Callable

from django.utils.translation import get_language
from django.db.models import Model
from django.db.models.fields import Field
from django.conf import settings

from extends.bases import ExtendFieldDescriptor, ExtendModelOptions


def to_attribute(name, language_code=None):
    language = language_code or get_language()
    return re.sub(r"[^a-z0-9_]+", "_", (f"{name}_{language}").lower())


def translated_attrgetter(name, field):
    return lambda self: getattr(self, to_attribute(name, get_language() or field.attr_suffix[0]))


def translated_attrsetter(name, field):
    return lambda self, value: setattr(self, to_attribute(name), value)


def proxy_from_orm(
    translated_fields: dict[str, str],
    orm_call: Callable,
    *args,
    **kwargs,
) -> None:

    return orm_call(*args, **translated_fields, **kwargs)


class TranslatedField(ExtendFieldDescriptor):

    def __init__(
        self,
        field: Field,
        specific=None,
        *,
        attr_suffix=None,
        attrgetter=translated_attrgetter,
        attrsetter=translated_attrsetter,
    ) -> None:

        attr_suffix = list(attr_suffix or (lang[0] for lang in settings.LANGUAGES))
        super().__init__(
            field,
            specific,
            attr_suffix=attr_suffix,
            attrgetter=attrgetter,
            attrsetter=attrsetter,
        )

    def to_attribute(self, name: str, suffix: str | None = None) -> str:
        return to_attribute(name, language_code=suffix)

    def contribute_to_class(self, model_cls: Model, name: str) -> None:
        super().contribute_to_class(model_cls, name)
        ExtendModelOptions.install(model_cls, name, self)
