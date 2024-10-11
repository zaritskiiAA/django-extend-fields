# TODO: Добавить общий игнор.
try:
    import django  # noqa
except ModuleNotFoundError:  # pragma: no cover
    pass
else:
    from .fields import TranslatedField  # noqa
    from .bases import ExtendField, ExtendMetaBase, ConverterMixin, AutoConvert  # noqa
    from .opportunity import (  # noqa
        TextResultModel,
        DeeplTranslator,
        get_translator,
        LangsModel,
        BatchLangsModel,
        AWSLangsModel,
        AWSBatchLangsModel,
        AWSLanguageDetector,
        get_detector,
    )
    from .validators import Validator  # noqa
    from .exceptions import UndefinedMethodError  # noqa
