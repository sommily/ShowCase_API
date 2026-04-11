from django.db.models import Q
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from .models import ShowcaseProject
from .serializers import (
    ShowcaseProjectListSerializer,
    ShowcaseProjectDetailSerializer,
    SyncProjectSerializer,
)
from .permissions import InternalSyncTokenPermission


# ==================== 自定义分页类 ====================


class StandardResultsSetPagination(PageNumberPagination):
    """标准分页类，支持 page_size 参数"""

    page_size = 12
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.page.paginator.count,
                "page": self.page.number,
                "page_size": self.page.paginator.per_page,
                "results": data,
            }
        )


# ==================== 公共展示 API ====================


class ProjectListView(generics.ListAPIView):
    """
    GET /api/showcase/projects/
    项目列表接口，支持筛选和分页
    """

    serializer_class = ShowcaseProjectListSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = ShowcaseProject.objects.filter(is_published=True)

        # 筛选参数
        program = self.request.query_params.get("program")
        module = self.request.query_params.get("module")
        semester = self.request.query_params.get("semester")
        featured = self.request.query_params.get("featured")
        keyword = self.request.query_params.get("keyword")

        if program:
            queryset = queryset.filter(program_name__icontains=program)

        if module:
            queryset = queryset.filter(module_name__icontains=module)

        if semester:
            queryset = queryset.filter(semester__icontains=semester)

        if featured in ("1", "true", "True"):
            queryset = queryset.filter(is_featured=True)

        if keyword:
            queryset = queryset.filter(
                Q(title_zh__icontains=keyword)
                | Q(title_en__icontains=keyword)
                | Q(students__icontains=keyword)
                | Q(teachers__icontains=keyword)
            )

        # 排序：sort_order ASC, id DESC
        queryset = queryset.order_by("sort_order", "-id")

        return queryset


class ProjectDetailView(generics.RetrieveAPIView):
    """
    GET /api/showcase/projects/{id}/
    项目详情接口（按主键ID）
    """

    serializer_class = ShowcaseProjectDetailSerializer
    queryset = ShowcaseProject.objects.filter(is_published=True)
    lookup_field = "pk"


class ProjectByProjectIdView(generics.RetrieveAPIView):
    """
    GET /api/showcase/projects/by-project-id/{project_id}/
    按 project_id 查询单个项目
    """

    serializer_class = ShowcaseProjectDetailSerializer
    queryset = ShowcaseProject.objects.filter(is_published=True)
    lookup_field = "project_id"


class FeaturedProjectsView(APIView):
    """
    GET /api/showcase/projects/featured/
    推荐项目列表，不分页，默认返回前8条
    """

    def get(self, request):
        limit = int(request.query_params.get("limit", 8))
        queryset = ShowcaseProject.objects.filter(
            is_published=True, is_featured=True
        ).order_by("sort_order", "-id")[:limit]

        serializer = ShowcaseProjectListSerializer(queryset, many=True)
        return Response(serializer.data)


class FiltersView(APIView):
    """
    GET /api/showcase/filters/
    返回所有已发布项目中的 distinct programs, modules, semesters
    """

    def get(self, request):
        published_projects = ShowcaseProject.objects.filter(is_published=True)

        programs = list(
            published_projects.exclude(program_name__isnull=True)
            .exclude(program_name="")
            .values_list("program_name", flat=True)
            .distinct()
            .order_by("program_name")
        )

        modules = list(
            published_projects.exclude(module_name__isnull=True)
            .exclude(module_name="")
            .values_list("module_name", flat=True)
            .distinct()
            .order_by("module_name")
        )

        semesters = list(
            published_projects.exclude(semester__isnull=True)
            .exclude(semester="")
            .values_list("semester", flat=True)
            .distinct()
            .order_by("semester")
        )

        return Response(
            {"programs": programs, "modules": modules, "semesters": semesters}
        )


# ==================== 内部同步 API ====================


class SyncProjectView(APIView):
    """
    POST /api/internal/showcase/sync/
    单条项目同步接口（upsert）
    """

    permission_classes = [InternalSyncTokenPermission]

    def post(self, request):
        serializer = SyncProjectSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = serializer.validated_data
        project_id = data["project_id"]

        # 查找是否已存在
        try:
            project = ShowcaseProject.objects.get(project_id=project_id)
            action = "updated"
        except ShowcaseProject.DoesNotExist:
            project = ShowcaseProject(project_id=project_id)
            action = "created"

        # 可覆盖字段
        updatable_fields = [
            "program_name",
            "module_name",
            "course_name",
            "semester",
            "title_zh",
            "title_en",
            "background",
            "description",
            "features",
            "students",
            "teachers",
            "poster_image_url",
            "thumbnail_image_url",
            "youtube_url",
            "tags",
            "sheet_row_id",
        ]

        for field in updatable_fields:
            if field in data:
                value = data[field]
                # 处理空字符串转为 None（针对可为null的字段）
                if value == "":
                    value = None
                setattr(project, field, value)

        # 更新同步信息
        project.last_synced_at = timezone.now()
        project.sync_status = "synced"

        project.save()

        return Response(
            {
                "success": True,
                "action": action,
                "project_id": project_id,
                "id": project.id,
            }
        )


class BatchSyncView(APIView):
    """
    POST /api/internal/showcase/sync/batch/
    批量项目同步接口
    """

    permission_classes = [InternalSyncTokenPermission]

    def post(self, request):
        if not isinstance(request.data, list):
            return Response(
                {"success": False, "error": "请求体必须是数组"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        items = request.data
        total = len(items)
        created_count = 0
        updated_count = 0
        failed_count = 0
        errors = []

        # 可覆盖字段
        updatable_fields = [
            "program_name",
            "module_name",
            "course_name",
            "semester",
            "title_zh",
            "title_en",
            "background",
            "description",
            "features",
            "students",
            "teachers",
            "poster_image_url",
            "thumbnail_image_url",
            "youtube_url",
            "tags",
            "sheet_row_id",
        ]

        for index, item in enumerate(items):
            serializer = SyncProjectSerializer(data=item)
            if not serializer.is_valid():
                failed_count += 1
                errors.append(
                    {
                        "index": index,
                        "project_id": item.get("project_id", "unknown"),
                        "errors": serializer.errors,
                    }
                )
                continue

            data = serializer.validated_data
            project_id = data["project_id"]

            try:
                try:
                    project = ShowcaseProject.objects.get(project_id=project_id)
                    updated_count += 1
                except ShowcaseProject.DoesNotExist:
                    project = ShowcaseProject(project_id=project_id)
                    created_count += 1

                # 更新可覆盖字段
                for field in updatable_fields:
                    if field in data:
                        value = data[field]
                        if value == "":
                            value = None
                        setattr(project, field, value)

                # 更新同步信息
                project.last_synced_at = timezone.now()
                project.sync_status = "synced"

                project.save()

            except Exception as e:
                failed_count += 1
                errors.append(
                    {"index": index, "project_id": project_id, "errors": str(e)}
                )

        return Response(
            {
                "success": True,
                "total": total,
                "created": created_count,
                "updated": updated_count,
                "failed": failed_count,
                "errors": errors,
            }
        )
