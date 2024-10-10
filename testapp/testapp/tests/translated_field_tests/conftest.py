import pytest

from .factories import QuestionFactory


@pytest.fixture
def obj_with_trans_field():
    return QuestionFactory.create()


@pytest.fixture
def model_obj():
    return QuestionFactory.build()
