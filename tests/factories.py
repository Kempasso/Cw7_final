import datetime
import logging

import factory.django
from freezegun import freeze_time

from apps.core.models import User
from apps.goals.models import Board, BoardParticipant, Goal, GoalCategory, GoalComment

logger = logging.getLogger('main')


class DataBaseFactory(factory.django.DjangoModelFactory):

    @staticmethod
    @freeze_time('3333-01-01')
    def get_create():
        return datetime.datetime.now()

    @staticmethod
    @freeze_time('4444-01-01')
    def get_update():
        return datetime.datetime.now()

    created = get_create()
    updated = get_update()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('user_name')
    password = factory.Faker('password')


class BoardFactory(DataBaseFactory):
    class Meta:
        model = Board

    title = factory.Faker('name')
    is_deleted = False
    created = DataBaseFactory.created
    updated = DataBaseFactory.updated


class BoardParticipantFactory(DataBaseFactory):
    class Meta:
        model = BoardParticipant

    board = factory.SubFactory(BoardFactory)
    user = factory.SubFactory(UserFactory)
    role = factory.Iterator([1, 2, 3])
    created = DataBaseFactory.created
    updated = DataBaseFactory.updated


class GoalCategoryFactory(DataBaseFactory):
    class Meta:
        model = GoalCategory

    board = factory.SubFactory(BoardFactory)
    title = factory.Faker('name')
    user = factory.SubFactory(UserFactory)
    is_deleted = False


class GoalFactory(DataBaseFactory):
    class Meta:
        model = Goal

    title = factory.Faker('name')
    description = factory.Faker('text')
    category = factory.SubFactory(GoalCategoryFactory)
    due_date = None
    user = factory.SubFactory(UserFactory)
    status = factory.Iterator([1, 2, 3, 4])
    priority = factory.Iterator([1, 2, 3, 4])


class GoalCommentFactory(DataBaseFactory):
    class Meta:
        model = GoalComment

    text = factory.Faker('text')
    goal = factory.SubFactory(GoalFactory)
    user = factory.SubFactory(UserFactory)
