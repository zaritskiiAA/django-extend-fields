try:
    import django  # noqa
except ModuleNotFoundError:  # pragma: no cover
    pass
else:
    from .fields import TranslatedField, to_attribute  # noqa
    from .bases import ExtendField, ExtendMetaBase  # noqa
