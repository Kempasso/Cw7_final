import logging
from unittest.mock import ANY

import pytest
from django.urls import reverse

from apps.goals.models import Board, BoardParticipant
from apps.goals.serializer import BoardSerializer

logger = logging.getLogger('main')


@pytest.mark.django_db
class TestBoardList:
    url = reverse('apps.goals:board_list')
    date_format = '%Y-%m-%dT%H:%M:%S.%fZ'

    def test_get_board_list_not_auth(self, client):
        """Проверка на получение списка досок не аутентифицированным пользователем"""
        result = client.get(self.url)
        assert result.status_code == 403

    def test_get_board_list(self, get_auth_client, board, user, board_participant):
        """Проверка на получение списка досок аутентифицированным пользователем"""
        response = get_auth_client.get(self.url)
        expected_response = {
            'id': board.pk,
            'title': board.title,
            'created': board.created.strftime(self.date_format),
            'updated': board.updated.strftime(self.date_format),
            'is_deleted': False
        }
        assert response.status_code == 200
        assert response.data[0] == expected_response

    def test_get_board_list_alien(self, get_auth_client):
        """Проверка на получение списка досок аутентифицированным пользователем,
        но не являющегося участником этих досок"""

        response = get_auth_client.get(self.url)
        assert response.status_code == 200
        assert response.data == []


@pytest.mark.django_db
class TestBoardCreated:
    url_create = reverse('apps.goals:create_board')
    date_format = '%Y-%m-%dT%H:%M:%S.%fZ'

    def test_created_board_not_auth(self, client):
        """Доску может создать только аутентифицированный пользователь"""
        response = client.post(self.url_create, data={'title': 'Test_title'})
        assert response.status_code == 403

    def test_created_board_auth(self, get_auth_client):
        """
        Аутентифицированный пользователь может создать доску.
        Проверяем то что текущий user является создателем доски и его роль -- "Владелец"
        """
        response = get_auth_client.post(self.url_create, data={'title': 'Test_Board_created'})
        current_user = response.wsgi_request.user
        created_board = Board.objects.get(pk=response.data['id'])
        owner = BoardParticipant.objects.get(board_id=created_board.pk)

        expected_response = {
            'id': created_board.pk,
            'title': created_board.title,
            'created': created_board.created.strftime(self.date_format),
            'updated': created_board.updated.strftime(self.date_format),
            'is_deleted': False
        }
        assert response.status_code == 201
        assert response.json() == expected_response
        assert current_user == owner.user
        assert owner.role == 1

    @pytest.mark.parametrize('role', [1, 2, 3])
    def test_retrieve_update_board(self, get_auth_client, board, board_participant, role):
        """Редактировать доску может только владелец доски c role == 1"""
        response = get_auth_client.put(f'/goals/board/{board.pk}', data={'title': board.title})
        expected_response = {
            'id': board.pk,
            'participants': BoardSerializer(board).data['participants'],
            'title': board.title,
            'created': board.created.strftime(self.date_format),
            'updated': ANY,
            'is_deleted': False
        }
        if board_participant.role == 1:
            assert response.status_code == 200
            assert response.json() == expected_response
        else:
            assert response.status_code == 403

    @pytest.mark.django_db
    @pytest.mark.parametrize('role', [1, 2, 3])
    def test_delete_board(self, get_auth_client, board, board_participant, role):
        """Доску может удалить только владелец у которого role = 1"""
        response = get_auth_client.delete(f'/goals/board/{board.pk}')
        deleted_board = Board.objects.get(pk=board.pk)

        if board_participant.role == 1:
            assert response.status_code == 204
            assert deleted_board.is_deleted
        else:
            assert response.status_code == 403
