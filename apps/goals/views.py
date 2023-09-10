from __future__ import annotations

from django.db import transaction
from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.goals.filters import GoalDateFilter
from apps.goals.models import Board, BoardParticipant, Goal, GoalCategory, GoalComment
from apps.goals.permissions import BoardPermission, GoalCategoryPermission, GoalPermission
from apps.goals.serializer import (BoardCreateSerializer,
                                   BoardListSerializer,
                                   BoardSerializer,
                                   CommentCreateSerializer,
                                   CommentSerializer,
                                   GoalCategoryCreateSerializer,
                                   GoalCategorySerializer,
                                   GoalCreateSerializer,
                                   GoalSerializer,)


class BoardCreateView(generics.CreateAPIView):
    """Создание новой доски"""
    serializer_class = BoardCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer) -> None:
        """Делаем текущего пользователя владельцем доски"""
        BoardParticipant.objects.create(user=self.request.user, board=serializer.save())


class BoardListView(generics.ListAPIView):
    """Получение списка досок пользователя"""
    serializer_class = BoardListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering = ['title']

    def get_queryset(self) -> Board:
        return Board.objects.filter(participants__user_id=self.request.user.id, is_deleted=False)


class BoardView(generics.RetrieveUpdateDestroyAPIView):
    """Редактирование и удаление досок пользователя"""
    permission_classes = [permissions.IsAuthenticated, BoardPermission]
    serializer_class = BoardSerializer

    def get_queryset(self) -> Board:
        return Board.objects.prefetch_related('participants__user').filter(is_deleted=False)

    def perform_destroy(self, instance: Board) -> Board:
        """Удаление доски (перевод is_deleted в True)"""
        with transaction.atomic():
            instance.is_deleted = True
            instance.save()
            instance.categories.update(is_deleted=True)
            Goal.objects.filter(category__board=instance).update(
                status=Goal.Status.archived
            )
        return instance


class GoalCategoryCreateView(generics.CreateAPIView):
    """Создание новой категории"""
    permission_classes = [GoalCategoryPermission]
    serializer_class = GoalCategoryCreateSerializer


class GoalCategoryListView(generics.ListAPIView):
    """Получение списка категорий где текущий user является участником"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCategorySerializer

    filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]
    ordering_fields = ('title', 'created')
    ordering = ['title']  # Не работает сортировка с front-end с DRF работает
    filterset_fields = ['board']
    search_fields = ['title']

    def get_queryset(self) -> GoalCategory:
        """Получение категорий в которых текущий пользователь является участником"""
        user = self.request.user
        return GoalCategory.objects.select_related('user').filter(board__participants__user_id=user.id,
                                                                  is_deleted=False)


class GoalCategoryView(generics.RetrieveUpdateDestroyAPIView):
    """Редактирование и удаление категории"""
    permission_classes = [GoalCategoryPermission]
    serializer_class = GoalCategorySerializer

    def get_queryset(self) -> GoalCategory:
        """Получение категорий в которых текущий пользователь является автором или редактором"""
        user = self.request.user
        return GoalCategory.objects.select_related('user').filter(board__participants__user_id=user.id,
                                                                  is_deleted=False)

    def perform_destroy(self, instance: GoalCategory) -> None:
        """Удаление категории (перевод is_deleted в True)"""
        with transaction.atomic():
            instance.is_deleted = True
            instance.save(update_fields=('is_deleted',))
            instance.goals.update(status=Goal.Status.archived)


class GoalCreateView(generics.CreateAPIView):
    """Создание цели у категории"""
    permission_classes = [GoalPermission]
    serializer_class = GoalCreateSerializer


class GoalListView(generics.ListAPIView):
    """Получение списка целей"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = GoalDateFilter
    ordering_fields = ('title', 'created')
    ordering = ['title']
    search_fields = ('title', 'description')

    def get_queryset(self) -> Goal:
        user = self.request.user
        return Goal.objects.select_related('user').filter(category__board__participants__user_id=user.id,
                                                          category__is_deleted=False
                                                          ).exclude(status=Goal.Status.archived)


class GoalView(generics.RetrieveUpdateDestroyAPIView):
    """Редактирование и удаление целей"""
    permission_classes = [GoalPermission]
    serializer_class = GoalSerializer

    def get_queryset(self) -> Goal:
        user = self.request.user
        return Goal.objects.select_related('user').filter(category__board__participants__user_id=user.id,
                                                          category__is_deleted=False
                                                          ).exclude(status=Goal.Status.archived)

    def perform_destroy(self, instance: Goal) -> None:
        instance.status = Goal.Status.archived
        instance.save(update_fields=('status',))


class GoalCommentCreateView(generics.CreateAPIView):
    """Создание комментария у цели"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentCreateSerializer

    def get_queryset(self) -> GoalComment:
        return GoalComment.objects.select_related('user').filter(user=self.request.user)


class GoalCommentView(generics.RetrieveUpdateDestroyAPIView):
    """Редактирование и удаление комментария"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentSerializer

    def get_queryset(self) -> GoalComment:
        return GoalComment.objects.select_related('user').filter(user=self.request.user)


class GoalCommentListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['goal']
    ordering = ['-created', '-updated']

    def get_queryset(self) -> GoalComment:
        user = self.request.user
        return GoalComment.objects.select_related('user').filter(goal__category__board__participants__user_id=user.id)
