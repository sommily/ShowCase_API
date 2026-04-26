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
        "api/showcase/projects/awards/",
        views.AwardWinnersView.as_view(),
        name="project-awards",
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
    path(
        "api/showcase/projects/<int:pk>/like/",
        views.ProjectLikeView.as_view(),
        name="project-like",
    ),
    path(
        "api/showcase/projects/<int:pk>/view/",
        views.ProjectViewCountView.as_view(),
        name="project-view-count",
    ),
    path(
        "api/showcase/academic-years/",
        views.AcademicYearsView.as_view(),
        name="academic-years",
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
