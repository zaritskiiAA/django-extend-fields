import factory

from testapp.models import Question


class QuestionFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Question
