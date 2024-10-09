from django.db import models
from django.utils.translation import gettext_lazy as _

from extends import TranslatedField, ExtendMetaBase
from extends.opportunity import get_translator


class Question(models.Model):

    question = TranslatedField(
        models.CharField(_("question"), max_length=200),
        auto=(get_translator, []),
    )
    answer = TranslatedField(
        models.CharField(_("answer"), max_length=200),
    )
    required_field = models.CharField(_("any_char_field"), max_length=200)
    default_field = models.IntegerField(_("any_int_field"), default=10)

    class ExtendMeta(ExtendMetaBase):
        override_query = True

    def __str__(self):
        return self.question
