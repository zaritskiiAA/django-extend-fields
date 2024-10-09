try:
    import django  # noqa
except ModuleNotFoundError:  # pragma: no cover
    pass
else:
    from .fields import TranslatedField, to_attribute  # noqa
    from .bases import ExtendField, ExtendMetaBase, ConverterMixin, AutoConvert  # noqa
    from .opportunity import TextResultModel, DeeplTranslator, get_translator  # noqa
