import types

import pytest
from django.utils.translation import override

from testapp.models import Question


@pytest.mark.django_db(transaction=True)
class TestTranslatedField:

    @pytest.mark.parametrize('attr', ('question', 'answer'))
    def test_getter(self, model_obj, attr):

        desc = getattr(Question, attr)

        for code in desc.attr_suffix:
            with override(code):
                assert not isinstance(
                    getattr(model_obj, attr, None), types.NoneType
                ), f'Translated Field getter dont returned required attr {attr}'

    @pytest.mark.parametrize(
        'attr, method, input_data', [
            ('question', 'create', 'hi'), ('question', 'update', 'hello')
        ]
    )
    def test_setter(self, attr, method, input_data, model_obj):

        desc = getattr(Question, attr)
        q = Question(**{attr: input_data})
        if method == 'update':
            q = model_obj
            setattr(q, attr, input_data)
        assert (
            getattr(q, desc.to_attribute(attr)) == input_data
        ), f'Tranlated Field setter dont set correct value {attr}, {input_data}'

    @pytest.mark.parametrize(
        'method, attr, input_data, expect_result',
            [
                ('create', 'question', 'hello', ('hello', 'Здравствуйте', 'hallo')),
                ('update', 'question', 'hello', ('hello', 'Здравствуйте', 'hallo')),
            ],
    )
    def test_auto_translation(self, method, attr, input_data, expect_result, obj_with_trans_field):

        desc = getattr(Question, attr)

        if method == 'create':
            q = Question(**{attr: input_data})
        if method == 'update':
            q = obj_with_trans_field
            setattr(obj_with_trans_field, attr, input_data)

            for expect, suf in zip(expect_result, desc.auto.suffix):
                raw_field = desc.to_attribute(attr, suffix=suf)
                result = getattr(q, raw_field, None)
                assert result, f'Auto-translated work incorrect. Dont set required field {raw_field}' # noqa E501
                assert result == expect, (
                    f'Auto translated work incorrect expect {expect}, now {result}'
                )
