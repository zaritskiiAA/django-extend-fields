import pytest
from django.conf import settings

from testapp.models import Question
from .factories import QuestionFactory
from extends import to_attribute


@pytest.mark.django_db(transaction=True)
class TestOverrideQuerySetInterface:

    # TODO: надо перегружать константу LANGUAGES на тестовую.
    @pytest.mark.parametrize('attr, value', [('question', 'question'), ('answer', 'answer')])
    def test_create_method(self, attr, value):

        test_obj = QuestionFactory.create(**{attr: value})

        assert (
            getattr(test_obj, to_attribute(attr)) == value
        ), f'Object {test_obj} with data {attr, value} installed incorrectly.'

        for code, _ in settings.LANGUAGES:
            assert hasattr(
                test_obj, to_attribute(attr, code)
            ), f'Transalted field must set table attr for obj {test_obj}.'

    @pytest.mark.parametrize(
        'attr, value', [('question', 'next_question'), ('answer', 'next_answer')]
    )
    def test_update_method(self, obj_with_trans_field, attr, value):

        Question.objects.update(**{attr: value})
        try:
            obj_after_update = Question.objects.get(id=obj_with_trans_field.id)
        except Question.DoesNotExist:
            raise AssertionError('After query update object does not exists.')

        assert getattr(obj_with_trans_field, to_attribute(attr)) != getattr(
            obj_after_update, to_attribute(attr)
        ), f'Object {obj_with_trans_field} attr {attr} not updated.'  # noqa E501
