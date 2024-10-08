import types

import pytest
from django.utils.translation import override
from django.conf import settings

from extends import to_attribute


@pytest.mark.django_db(transaction=True)
class TestTranslatedField:

    @pytest.mark.parametrize('attr', ('question', 'answer'))
    def test_getter(self, obj_with_trans_field, attr):

        for code, _ in settings.LANGUAGES:
            with override(code):
                assert not isinstance(
                    getattr(obj_with_trans_field, attr, None), types.NoneType
                ), f'Translated Field getter dont returned required attr {attr}'

    @pytest.mark.parametrize(
        'attr, value', [('question', 'next_question'), ('answer', 'next_answer')]
    )
    def test_setter(self, obj_with_trans_field, attr, value):

        setattr(obj_with_trans_field, attr, value)

        assert (
            getattr(obj_with_trans_field, to_attribute(attr)) == value
        ), f'Tranlated Field setter dont set correct value {attr}, {value}'
