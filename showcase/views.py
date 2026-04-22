from django.db import models
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
        major = self.request.query_params.get("major")
        semester = self.request.query_params.get("semester")
        featured = self.request.query_params.get("featured")
        keyword = self.request.query_params.get("keyword")

        if major:
            queryset = queryset.filter(major=major)

        if semester:
            queryset = queryset.filter(semester__icontains=semester)

        if featured in ("1", "true", "True"):
            queryset = queryset.filter(is_featured=True)

        if keyword:
            queryset = queryset.filter(
                Q(project_title_cn__icontains=keyword)
                | Q(project_title_en__icontains=keyword)
                | Q(project_id__icontains=keyword)
                | Q(students__icontains=keyword)
                | Q(ib_instructors__icontains=keyword)
                | Q(fa_instructors__icontains=keyword)
                | Q(tm_instructors__icontains=keyword)
                | Q(ge_instructors__icontains=keyword)
                | Q(cd_instructors__icontains=keyword)
                | Q(ca_instructors__icontains=keyword)
            )

        # 学年筛选
        academic_year = self.request.query_params.get("academic_year")
        if academic_year:
            queryset = queryset.filter(academic_year=academic_year)

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


class AcademicYearsView(APIView):
    """返回所有学年列表及其状态"""

    def get(self, request):
        # 获取所有已发布项目中的 distinct 学年
        years = (
            ShowcaseProject.objects.filter(is_published=True)
            .values_list("academic_year", flat=True)
            .distinct()
            .order_by("-academic_year")
        )

        years_list = list(years)
        current_year = max(years_list) if years_list else 2025

        result = {
            "current_year": current_year,
            "years": [
                {
                    "year": y,
                    "status": "ongoing" if y == current_year else "completed",
                    "label": (
                        f"{y}学年评选（进行中）"
                        if y == current_year
                        else f"{y}学年评选"
                    ),
                }
                for y in years_list
            ],
        }
        return Response(result)


class AwardWinnersView(generics.ListAPIView):
    """返回指定学年的获奖作品"""

    serializer_class = ShowcaseProjectListSerializer
    pagination_class = None  # 不分页

    def get_queryset(self):
        queryset = ShowcaseProject.objects.filter(
            is_published=True,
            award_level__isnull=False,
        )

        academic_year = self.request.query_params.get("academic_year")
        if academic_year:
            queryset = queryset.filter(academic_year=academic_year)

        # 判断是否是当期学年（最大学年）
        max_year = ShowcaseProject.objects.filter(is_published=True).aggregate(
            max_year=models.Max("academic_year")
        )["max_year"]

        # 当期学年不返回获奖数据
        if academic_year and int(academic_year) == max_year:
            return ShowcaseProject.objects.none()

        return queryset.order_by("award_level", "sort_order")


class FiltersView(APIView):
    """
    GET /api/showcase/filters/
    返回所有已发布项目中的 distinct programs, modules, semesters
    """

    def get(self, request):
        published_projects = ShowcaseProject.objects.filter(is_published=True)

        majors = list(
            published_projects.exclude(major__isnull=True)
            .exclude(major="")
            .values_list("major", flat=True)
            .distinct()
            .order_by("major")
        )

        semesters = list(
            published_projects.exclude(semester__isnull=True)
            .exclude(semester="")
            .values_list("semester", flat=True)
            .distinct()
            .order_by("semester")
        )

        academic_years = list(
            published_projects.values_list("academic_year", flat=True)
            .distinct()
            .order_by("-academic_year")
        )

        return Response(
            {
                "programs": majors,
                "semesters": semesters,
                "academic_years": academic_years,
            }
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
            "major",
            "semester",
            "project_title_cn",
            "project_title_en",
            "project_intro",
            "project_description",
            "features",
            "students",
            "ib_course",
            "ib_instructors",
            "fa_course",
            "fa_instructors",
            "tm_course",
            "tm_instructors",
            "ge_course",
            "ge_instructors",
            "cd_course",
            "cd_instructors",
            "ca_course",
            "ca_instructors",
            "poster_url",
            "thumbnail_url",
            "youtube_url",
            "tags",
            "google_sheet_row_number",
            "academic_year",
            "award_level",
            "poster_file_id",
            "poster_file_url",
            "thumbnail_file_id",
            "thumbnail_file_url",
            "submit_timestamp",
            "email",
        ]

        for field in updatable_fields:
            if field in data:
                value = data[field]
                # 处理空字符串转为 None（针对可为null的字段）
                if value == "":
                    value = None
                setattr(project, field, value)

        # 更新同步信息
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
            "major",
            "semester",
            "project_title_cn",
            "project_title_en",
            "project_intro",
            "project_description",
            "features",
            "students",
            "ib_course",
            "ib_instructors",
            "fa_course",
            "fa_instructors",
            "tm_course",
            "tm_instructors",
            "ge_course",
            "ge_instructors",
            "cd_course",
            "cd_instructors",
            "ca_course",
            "ca_instructors",
            "poster_url",
            "thumbnail_url",
            "youtube_url",
            "tags",
            "google_sheet_row_number",
            "academic_year",
            "award_level",
            "poster_file_id",
            "poster_file_url",
            "thumbnail_file_id",
            "thumbnail_file_url",
            "submit_timestamp",
            "email",
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
