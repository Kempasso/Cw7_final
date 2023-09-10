import logging
from unittest.mock import ANY

import pytest

from apps.core.serializer import ProfileSerializer
from apps.goals.models import Goal
from tests.factories import GoalCommentFactory

logger = logging.getLogger('main')


@pytest.mark.django_db
class TestComment:

    @pytest.mark.parametrize('role', (1, 2, 3))
    def test_create_comment_auth(self, get_auth_client, goal, board_participant, role):
        """Комментарии у цели может создавать только участник с role 1 и 2 (владелец и редактор)"""
        response = get_auth_client.post('/goals/goal_comment/create', data={
            'text': 'Test comment',
            'goal': goal.pk
        })

        test_goal = Goal.objects.get(user_id=response.wsgi_request.user.pk)

        expected_response = {
            'text': 'Test comment',
            'goal': test_goal.pk
        }
        if board_participant.role in (1, 2):  # TODO Bad Request: /goals/goal_comment/create
            assert response.status_code == 201
            assert response.data == expected_response
        else:
            assert response.status_code == 403

    def test_create_comment_not_auth(self, client, goal):
        """Комментарии может отставлять только аутентифицированный пользователь"""
        response = client.post('/goals/goal_comment/create', data={
            'text': 'Test comment',
            'goal': goal.pk
        })
        assert response.status_code == 403

    def test_update_comment(self, get_auth_client, goal_comment):
        """
        Редактировать комментарий может только автор, остальные пользователи не могут перейти на страницу
        редактирования
        """
        goal_comment_not_author = GoalCommentFactory.create_batch(1)
        response_not_author = get_auth_client.put(f'/goals/goal_comment/{goal_comment_not_author[0].pk}',
                                                  data={'text': 'Test_update_comment'})
        response_author = get_auth_client.put(f'/goals/goal_comment/{goal_comment.pk}',
                                              data={'text': 'Test_update_comment'})
        expected_response = {
            'id': goal_comment.pk,
            'user': ProfileSerializer(goal_comment.user).data,
            'updated': ANY,
            'created': ANY,
            'text': 'Test_update_comment',
            'goal': goal_comment.goal.pk
        }

        assert response_author.status_code == 200
        assert response_author.json() == expected_response
        assert response_not_author.status_code == 404

    def test_delete_comment(self, get_auth_client, goal_comment):
        """Удалить комментарий может только автор, остальные пользователи не могут перейти на страницу удаления"""
        goal_comment_not_author = GoalCommentFactory.create_batch(1)
        response_not_author = get_auth_client.delete(f'/goals/goal_comment/{goal_comment_not_author[0].pk}')
        response_author = get_auth_client.delete(f'/goals/goal_comment/{goal_comment.pk}')

        assert response_not_author.status_code == 404
        assert response_author.status_code == 204
