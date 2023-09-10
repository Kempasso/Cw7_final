from __future__ import annotations

from django.urls import path

from apps.goals import views

urlpatterns = [
    # Board
    path('board/create', views.BoardCreateView.as_view(), name='create_board'),
    path('board/list', views.BoardListView.as_view(), name='board_list'),
    path('board/<int:pk>', views.BoardView.as_view(), name='board'),

    # Goal Category API
    path('goal_category/create', views.GoalCategoryCreateView.as_view(), name='create_category'),
    path('goal_category/list', views.GoalCategoryListView.as_view(), name='category_list'),
    path('goal_category/<int:pk>', views.GoalCategoryView.as_view(), name='goal_category'),

    # Goals API
    path('goal/create', views.GoalCreateView.as_view(), name='create_goal'),
    path('goal/list', views.GoalListView.as_view(), name='goal_list'),
    path('goal/<int:pk>', views.GoalView.as_view(), name='goal'),

    # Goal Comment API
    path('goal_comment/create', views.GoalCommentCreateView.as_view(), name='create_comment'),
    path('goal_comment/list', views.GoalCommentListView.as_view(), name='goal_list'),
    path('goal_comment/<pk>', views.GoalCommentView.as_view(), name='comment'),
]
