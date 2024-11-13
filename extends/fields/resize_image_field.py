import re
from typing import Callable, Any, Iterable

from django.db.models import Model, ImageField

from extends.bases import ExtendFieldDescriptor, ExtendModelOptions


def to_attribute(name, resolution=None):
    return re.sub(r"[^a-z0-9_]+", "_", (f"{name}_{resolution}").lower())


def translated_attrgetter(name, field):
    return lambda self: getattr(self, to_attribute(name, field.attr_suffix[0]))


def translated_attrsetter(name, field):

    def _setter(self, value):

        for v in field.validators:
            v.validate(value)

        if hasattr(field, '_auto'):
            pass
        else:
            setattr(self, to_attribute(name, field.attr_suffix[0]), value)

    return _setter


def _to_orm(desc_kwargs: dict[str, str], orm_call: Callable[..., Any], *args, **kwargs) -> Any:

    pass


class ResizeImageField(ExtendFieldDescriptor):

    def __init__(
        self,
        field: ImageField,
        resolution: Iterable[str],
        specific=None,
        *,
        attrgetter=translated_attrgetter,
        attrsetter=translated_attrsetter,
        validators=None,
    ) -> None:

        resolution = list(resolution)

        super().__init__(
            field,
            specific,
            attr_suffix=resolution,
            attrgetter=attrgetter,
            attrsetter=attrsetter,
            validators=validators,
        )

    def to_attribute(self, name: str, suffix: str | None = None) -> str:
        res = suffix or self.attr_suffix[0]
        return to_attribute(name, resolution=res)

    def contribute_to_class(self, model_cls: Model, name: str) -> None:
        super().contribute_to_class(model_cls, name)
        ExtendModelOptions.install(model_cls, name, self, orm_proxy=_to_orm)