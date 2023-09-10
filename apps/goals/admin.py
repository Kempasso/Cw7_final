from __future__ import annotations

from django.contrib import admin

from apps.goals.models import Board, Goal, GoalCategory, GoalComment


@admin.register(GoalCategory)
class GoalCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created', 'updated')
    search_fields = ('title', 'user__username')
    list_filter = ('is_deleted',)
    search_help_text = 'Поиск по названию категории и имени пользователя'


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created', 'updated',)
    search_fields = ('title', 'description',)
    list_filter = ('status',)
    search_help_text = 'Поиск по названию и описанию цели'


@admin.register(GoalComment)
class GoalComment(admin.ModelAdmin):
    list_display = ('goal', 'user', 'created', 'updated',)
    search_fields = ('text',)
    list_filter = ('goal',)
    search_help_text = 'Поиск по тексту в комментарии'


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('title', 'created', 'updated', 'is_deleted',)
    search_fields = ('title',)
    list_filter = ('title', 'is_deleted',)
    search_help_text = 'Поиск по названию доски'
