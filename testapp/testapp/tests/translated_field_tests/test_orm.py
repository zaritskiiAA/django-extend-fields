import pytest

from testapp.models import Question
from .factories import QuestionFactory


@pytest.mark.django_db(transaction=True)
class TestOverrideQuerySetInterface:

    @pytest.mark.parametrize('attr, value', [('question', 'question'), ('answer', 'answer')])
    def test_create_method(self, attr, value):

        test_obj = QuestionFactory.create(**{attr: value})
        desc = getattr(Question, attr)

        assert (
            getattr(test_obj, desc.to_attribute(attr)) == value
        ), f'Object {test_obj} with data {attr, value} installed incorrectly.'

        for code in desc.attr_suffix:
            assert hasattr(
                test_obj, desc.to_attribute(attr, code)
            ), f'Transalted field must set table attr for obj {test_obj}.'

    @pytest.mark.parametrize(
        'attr, value', [('question', 'next_question'), ('answer', 'next_answer')]
    )
    def test_update_method(self, obj_with_trans_field, attr, value):

        Question.objects.update(**{attr: value})
        desc = getattr(Question, attr)

        try:
            obj_after_update = Question.objects.get(id=obj_with_trans_field.id)
        except Question.DoesNotExist:
            raise AssertionError('After query update object does not exists.')

        assert getattr(obj_with_trans_field, desc.to_attribute(attr)) != getattr(
            obj_after_update, desc.to_attribute(attr)
        ), f'Object {obj_with_trans_field} attr {attr} not updated.'  # noqa E501

    @pytest.mark.parametrize(
            'method, attr, input_data, expect_result',
            [
                ('create', 'question', 'hello', ('hello', 'Здравствуйте', 'hallo')),
                ('update', 'question', 'hello', ('hello', 'Здравствуйте', 'hallo')),
            ],
    )
    def test_auto_translation(self, obj_with_trans_field, method, attr, input_data, expect_result):
        desc = getattr(Question, attr)

        if method == 'update':
            id = obj_with_trans_field.id
            Question.objects.update(**{attr: input_data})
            q = Question.objects.get(id=id)
        if method == 'create':
            q = Question.objects.create(**{attr: input_data})

            for expect, suf in zip(expect_result, desc.auto.suffix):
                raw_field = desc.to_attribute(attr, suffix=suf)
                result = getattr(q, raw_field, None)
                assert result, f'Auto-translated work incorrect. Dont set required field {raw_field}' # noqa E501
                assert result == expect, (
                    f'Auto translated work incorrect expect {expect}, now {result}'
                )
