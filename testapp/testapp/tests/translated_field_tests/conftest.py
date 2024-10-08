import pytest

from .factories import QuestionFactory


@pytest.fixture
def obj_with_trans_field():
    return QuestionFactory.create()
