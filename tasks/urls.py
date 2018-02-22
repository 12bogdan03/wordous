from django.urls import path

from . import views

app_name = 'tasks'
urlpatterns = [
    path('<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
    path('create/', views.TaskCreateView.as_view(), name='task_create'),
    path('<int:pk>/update/', views.TaskUpdateView.as_view(),
         name='task_update'),
    path('<int:pk>/delete/', views.TaskDeleteView.as_view(),
         name='task_delete'),
    path('<int:pk>/execute/', views.TaskExecuteView.as_view(),
         name='task_execute'),
    path('<int:pk>/become-executor/', views.BecomeTaskExecutorView.as_view(),
         name='become_task_executor'),
    path('<int:task_id>/comment/', views.CommentCreateView.as_view(),
         name='comment_create'),
    path('<str:kind>/', views.TaskListView.as_view(), name='task_list'),
    path('', views.TaskListView.as_view(), name='task_list'),
]
