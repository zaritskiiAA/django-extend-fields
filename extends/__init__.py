# TODO: Добавить общий игнор.
try:
    import django  # noqa
except ModuleNotFoundError:  # pragma: no cover
    pass
else:
    from .fields import TranslatedField  # noqa
    from .bases import ExtendField, ExtendMetaBase, ConverterMixin, AutoConvert  # noqa
    from .opportunity import ( # noqa
        TextResultModel, DeeplTranslator, get_translator, # noqa
        LangsModel, AWSLanguageDetector, get_detector, # noqa
    )
    from .validators import Validator # noqa
