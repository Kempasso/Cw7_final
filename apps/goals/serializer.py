from __future__ import annotations

import logging

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.core.models import User
from apps.core.serializer import ProfileSerializer
from apps.goals.models import Board, BoardParticipant, Goal, GoalCategory, GoalComment

logger = logging.getLogger('main')


class BoardCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания новой доски"""
    class Meta:
        model = Board
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'is_deleted')


class BoardParticipantSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(required=True, choices=BoardParticipant.Role.choices[1:])
    user = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())

    class Meta:
        model = BoardParticipant
        fields = ('id', 'user', 'board', 'role')
        read_only_fields = ('id', 'created', 'updated', 'board')


class BoardSerializer(serializers.ModelSerializer):
    """Сериализатор для редактирования и удаления доски"""
    participants = BoardParticipantSerializer(many=True, required=False)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Board
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'is_deleted')

    def update(self, instance: Board, validated_data: dict) -> Board:
        """Добавление новых участников и изменение названия доски """
        participants_data = validated_data.pop('participants', None)
        owner_id = self.context['request'].user.id
        if participants_data:
            new_participants = {part['user'].id: part for part in participants_data}
            with transaction.atomic():
                for old_participant in instance.participants.exclude(user=owner_id):
                    if old_participant.user_id not in new_participants:
                        old_participant.delete()
                    else:
                        new_part = new_participants[old_participant.user_id]
                        if old_participant.role != new_part['role']:
                            old_participant.role = new_part['role']
                            old_participant.save()
                        new_participants.pop(old_participant.user_id)

                for new_part in new_participants.values():
                    BoardParticipant.objects.create(
                        board=instance,
                        user=new_part['user'],
                        role=new_part['role']
                    )

        else:
            BoardParticipant.objects.filter(board=instance).delete()
            BoardParticipant.objects.update_or_create(board=instance,
                                                      user=self.context['request'].user,
                                                      role=1)

        if title := validated_data.get('title'):
            instance.title = title

        instance.save()

        return instance


class BoardListSerializer(serializers.ModelSerializer):
    """Сериализатор списка досок пользователя"""
    class Meta:
        model = Board
        fields = '__all__'


class GoalCategoryCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания новой категории"""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate_board(self, board: Board) -> Board:
        """Валидация на создание категории только для не удаленных досок и на то что юзер автор или редактор доски"""
        if board.is_deleted:
            raise serializers.ValidationError('board is delete')
        if not BoardParticipant.objects.filter(
                board_id=board.id,
                user_id=self.context['request'].user.id,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer]
        ).exists():
            raise PermissionDenied
        return board

    class Meta:
        model = GoalCategory
        read_only_fields = ('id', 'created', 'updated', 'user', 'is_deleted')
        fields = '__all__'


class GoalCategorySerializer(serializers.ModelSerializer):
    """Сериализатор получения списка категорий"""
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = GoalCategory
        read_only_fields = ('id', 'created', 'updated', 'user', 'is_deleted')
        fields = '__all__'


class GoalCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания цели у категории"""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user')

    def validate_category(self, category: GoalCategory) -> GoalCategory:
        """Валидация на то что user является автором или редактором, и то что категория не удалена"""
        if category.is_deleted:
            raise serializers.ValidationError('not allowed in deleted category')

        if not BoardParticipant.objects.filter(
                board_id=category.board_id,
                user_id=self.context['request'].user.id,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer]
        ).exists():
            raise PermissionDenied

        return category


class GoalSerializer(serializers.ModelSerializer):
    """Сериализатор для редактирования и удаления целей"""
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = Goal
        read_only_fields = ('id', 'created', 'updated', 'user')
        fields = '__all__'

    def validate_category(self, value: GoalCategory) -> GoalCategory:
        if value.is_deleted:
            raise serializers.ValidationError('not allowed in deleted category')

        if value.user != self.context['request'].user:
            raise PermissionDenied

        return value


class CommentCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания комментариев"""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalComment
        fields = ('text', 'goal', 'user')
        read_only_fields = ('id', 'created', 'updated', 'user')

    def validate_goal(self, value: Goal) -> Goal:
        if value.status == Goal.Status.archived:
            raise ValidationError('Goal not found')
        if not BoardParticipant.objects.filter(
                board_id=value.category.board_id,
                role__in=[
                    BoardParticipant.Role.owner, BoardParticipant.Role.writer
                ],
                user=self.context['request'].user,
        ).exists():
            raise PermissionDenied
        return value


class CommentSerializer(serializers.ModelSerializer):
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = GoalComment
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'goal', 'user')

    def validate_comment(self, value: GoalComment) -> GoalComment:
        if value.user != self.context['request'].user:
            raise PermissionDenied
        return value
