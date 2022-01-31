from django.urls import path
from . import views

app_name = 'task'
urlpatterns = [
    path('', views.ToppageView.as_view(), name="toppage"),
    path('user_list', views.UserListView.as_view(), name="user_list"),
    path('user-create/', views.UserCreateView.as_view(), name="user_create"),
    path('user-info/<int:pk>/', views.UserInfoView.as_view(), name="user_info"),
    path('<int:pk>/', views.UserInfoView.user_info, name="user_info_pop"),
    path('user-edit/<int:pk>/', views.UserEditView.as_view(), name="user_edit"),
    path('class-list/', views.ClassListView.as_view(), name="class_list"),
    path('class-create/', views.ClassCreateView.as_view(), name="class_create"),
    path('class-info/<int:pk>/', views.ClassInfoView.as_view(), name="class_info"),
    path('<int:pk>/', views.ClassInfoView.class_info, name="class_info_pop"),
    path('class-edit/<int:pk>/', views.ClassEditView.as_view(), name="class_edit"),
    path('task-list/', views.TaskListView.as_view(), name="task_list"),
    path('task-create/', views.TaskCreateView.as_view(), name="task_create"),
    path('task-info/<int:pk>/', views.TaskInfoView.as_view(), name="task_info"),
    path('task-edit/<int:pk>/', views.TaskEditView.as_view(), name="task_edit"),
    path('task-info/<int:pk>/task-set/',
         views.TaskSetView.as_view(), name='task_set'),
    path('possible-task-list/', views.PossibleTaskListView.as_view(),
         name="possible_task_list"),
    path('task_exam/<int:pk>/', views.TakeExamView.as_view(), name="take_exam"),
    path('answer/<int:pk>', views.AnswerView.as_view(), name="answer"),
]
