from django.conf.urls import include, url
from rest_framework import routers
from django.urls import path
from . import views
from .views import BoardDetail, GithubWebhook, HomeView
from .viewsets import (
    BoardViewSet,
    ColumnViewSet,
    ProjectViewSet,
    TodoViewset,
    TypeViewSet,
    UserViewset,
    TagViewSet,
)

router = routers.DefaultRouter()
router.register(r"projects", ProjectViewSet)
router.register(r"boards", BoardViewSet)
router.register(r"columns", ColumnViewSet)
router.register(r"types", TypeViewSet)
router.register(r"tags", TagViewSet)
router.register(r"todos", TodoViewset)
router.register(r"users", UserViewset)

app_name = "budget"

urlpatterns = [
    path("boards/", views.boards, name="boards"),
    path("board/<str:pk>/", views.board, name="board"),
    path("create_board/", views.createBoard, name="make_board"),
    path("update_board/<str:pk>/", views.updateBoard, name="update_board"),
    path("delete_board/<str:pk>/", views.deleteBoard, name="delete_board"),
    path("projects/", views.projects, name="index"),
    path("project/<str:pk>/", views.project, name="details"),
    path("create_project/", views.createProject, name="make_project"),
    path("update_project/<str:pk>/", views.updateProject, name="update"),
    path("delete_project/<str:pk>/", views.deleteProject, name="delete"),
    url(r"^$", HomeView.as_view(), name="budget-boards"),
    url(r"^api/", include(router.urls)),
    url(r"^webhook/github/$", GithubWebhook.as_view()),
    url(r"^(?P<slug>[-\w]+)/$", BoardDetail.as_view(), name="budget-boards-detail"),
]
