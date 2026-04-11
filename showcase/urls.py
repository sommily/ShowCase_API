from django.urls import path
from . import views

app_name = "showcase"

urlpatterns = [
    # 公共展示 API
    path(
        "api/showcase/projects/", views.ProjectListView.as_view(), name="project-list"
    ),
    path(
        "api/showcase/projects/featured/",
        views.FeaturedProjectsView.as_view(),
        name="project-featured",
    ),
    path(
        "api/showcase/projects/by-project-id/<str:project_id>/",
        views.ProjectByProjectIdView.as_view(),
        name="project-by-project-id",
    ),
    path(
        "api/showcase/projects/<int:pk>/",
        views.ProjectDetailView.as_view(),
        name="project-detail",
    ),
    path("api/showcase/filters/", views.FiltersView.as_view(), name="filters"),
    # 内部同步 API
    path(
        "api/internal/showcase/sync/",
        views.SyncProjectView.as_view(),
        name="sync-project",
    ),
    path(
        "api/internal/showcase/sync/batch/",
        views.BatchSyncView.as_view(),
        name="sync-batch",
    ),
]
