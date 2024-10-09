from inspect import isclass
from abc import ABC, abstractmethod
from typing import Callable, Any
from collections import namedtuple
from contextvars import ContextVar
from contextlib import contextmanager

from django.db.models import Model
from django.db.models.fields import Field
from django.utils.functional import lazy
from django.utils.text import capfirst
from django.db.models.manager import Manager
from pydantic import BaseModel


_show_suffix = ContextVar("show_suffix")


@contextmanager
def show_suffix(show):
    token = _show_suffix.set(show)
    yield
    _show_suffix.reset(token)


class AbstractExtendField(ABC):

    @abstractmethod
    def contribute_to_class(self, model_cls: Model, name: str) -> None:
        pass

    @abstractmethod
    def to_attribute(name: str, suffix: str | None = None) -> str:
        pass


class AutoConvert:

    def __init__(self, converter: Callable[..., BaseModel], suffix: list[str]) -> None:

        self.converter = converter
        self.suffix = suffix


class ConverterMixin:

    def _create_auto_property(self, converter_data) -> None:

        self._auto = True

        def fget(self):

            if hasattr(self, '_auto'):
                return AutoConvert(*converter_data)

        setattr(self.__class__, 'auto', property(fget=fget))


class ExtendField(AbstractExtendField):

    def __init__(
        self,
        field: Field,
        specific=None,
        *,
        attr_suffix=None,
    ) -> None:

        self._field = field
        self._specific = specific or {}
        self.attr_suffix = attr_suffix

        self.creation_counter = Field.creation_counter
        Field.creation_counter += len(self.attr_suffix)

    @staticmethod
    def _verbose_name_maybe_suffix(verbose_name, suffix):
        def verbose_name_fn():
            if _show_suffix.get(False):
                return f"{capfirst(verbose_name)} [{suffix}]"
            return str(verbose_name)

        return lazy(verbose_name_fn, str)()

    def to_attribute(name: str, suffix: str | None = None) -> str:
        raise NotImplementedError(
            'Override this method or use proposed options in "_fields" modules.'
        )

    def contribute_to_class(self, model_cls: Model, name: str) -> None:

        _n, _p, args, kwargs = self._field.deconstruct()
        self.attrname = name
        fields = []
        verbose_name = kwargs.pop("verbose_name", name)
        for index, suffix in enumerate(self.attr_suffix):
            field_kw = dict(kwargs, **self._specific.get(suffix, {}))
            field_kw.setdefault(
                "verbose_name",
                self._verbose_name_maybe_suffix(verbose_name, suffix),
            )
            f = self._field.__class__(*args, **field_kw)
            f._suffix = suffix
            f.creation_counter = self.creation_counter + index
            attr = self.to_attribute(name, suffix)
            f.contribute_to_class(model_cls, attr)
            fields.append(attr)

        self.fields = fields
        self.short_description = verbose_name


class ExtendFieldDescriptor(ExtendField):

    def __init__(
        self,
        field: Field,
        specific=None,
        *,
        attr_suffix=None,
        attrgetter=None,
        attrsetter=None,
    ) -> None:

        super().__init__(field, specific, attr_suffix=attr_suffix)

        self._attrgetter = attrgetter
        self._attrsetter = attrsetter

    def contribute_to_class(self, model_cls: Model, name: str) -> None:
        super().contribute_to_class(model_cls, name)

        setattr(model_cls, name, self)

        self._getter = self._attrgetter(name, field=self)
        self._setter = self._attrsetter(name, field=self)

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return self._getter(obj)

    def __set__(self, obj, value):
        self._setter(obj, value)


class ExtendMetaBase:

    override_query: bool = False


class ExtendModelOptions:
    """Override/extend django fields opportunity."""

    from .manager_builder import ManagerBuilder

    manager_builder = ManagerBuilder
    models_data = {}

    @classmethod
    def _set_descriptor_to_django_model_meta(cls, model_cls):

        opts, name = cls.models_data[model_cls]['opts'], cls.models_data[model_cls]['extend_field']
        opts._property_names = frozenset(prop for prop in list(opts._property_names) + [name])

    @classmethod
    def _create_manager(cls, model_cls: Model) -> Manager:

        from .exceptions import ManagerBuilderExceptions, warning_message

        opts = cls.models_data[model_cls]['opts']

        if orm_proxy := cls.models_data[model_cls]['orm_proxy_method']:
            pass
        else:
            raise ValueError(
                'If you override django orm in ExtendMeta, ExtendModelOptions '
                'must get orm_proxy method. In default its extends.fields._to_orm.'
            )
        if ManagerBuilder := getattr(cls, 'manager_builder', None):

            builder = ManagerBuilder()
            opts.extend_descriptor = {}
            if 'objects' not in opts.managers_map:
                m = builder.create_manager(Manager())()
            else:
                m = builder.create_manager(opts.managers_map['objects'])()
                # Django installs managers through properties 'managers'
                # in Options object which collect them from
                # all parents and skiped duplicate names. That`s why before
                # we contibute our manager delete manager with 'objects' name.
                opts.local_managers = [
                    manag for manag in opts.local_managers if manag.name != 'objects'
                ]
            setattr(m, 'orm_proxy', orm_proxy)
            m.contribute_to_class(model_cls, 'objects')
            warning_message(f'Override django "objects" manager for {model_cls}.')
            return
        raise ManagerBuilderExceptions('ManagerBuilder does not exists.')

    @staticmethod
    def _find_extend_meta(model_cls: Model) -> ExtendMetaBase:

        ExtendMeta = namedtuple('ExtendMeta', 'name meta')
        overkill_meta_instance = 0
        for attr, obj in model_cls.__dict__.items():

            if isclass(obj) and issubclass(obj, ExtendMetaBase):

                if not overkill_meta_instance:
                    extend = ExtendMeta(attr, obj)
                overkill_meta_instance += 1

        if not overkill_meta_instance:
            return None

        if overkill_meta_instance > 1:
            raise ValueError(
                f'Django model can take 1 ExtendMeta class, but given {overkill_meta_instance}'
            )
        return extend

    @classmethod
    def install(
        cls,
        model_cls: Model,
        extend_field: str,
        extend_obj: ExtendField,
        orm_proxy: Callable[..., Any] = None,
    ) -> None:

        if model_cls not in cls.models_data and cls.models_data:
            cls.models_data = {}

        if not cls.models_data:
            extend_meta = cls._find_extend_meta(model_cls)
            cls.models_data[model_cls] = {
                "extend_field": extend_field,
                "extend_obj": extend_obj,
                "opts": model_cls._meta,
                "extend_meta": extend_meta,
                "orm_proxy_method": orm_proxy,
            }
            if extend_meta and extend_meta.meta.override_query:
                cls._create_manager(model_cls)
        else:
            cls.models_data[model_cls].update(
                {
                    "extend_field": extend_field,
                    "extend_obj": extend_obj,
                }
            )

        opts = cls.models_data[model_cls]["opts"]

        if hasattr(opts, "extend_descriptor"):
            cls._set_descriptor_to_django_model_meta(model_cls)
            opts.extend_descriptor[extend_field] = extend_obj
