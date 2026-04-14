from django.contrib import admin
from django.utils.html import format_html
from .models import ShowcaseProject


@admin.register(ShowcaseProject)
class ShowcaseProjectAdmin(admin.ModelAdmin):
    list_display = [
        "thumbnail_preview",
        "project_title_cn",
        "major",
        "semester",
        "academic_year",
        "award_level",
        "is_published",
        "is_featured",
        "sort_order",
        "updated_at",
    ]
    list_filter = [
        "major",
        "semester",
        "academic_year",
        "award_level",
        "is_published",
        "is_featured",
    ]
    search_fields = ["project_id", "project_title_cn", "project_title_en", "students"]
    list_editable = ["is_published", "is_featured", "sort_order", "award_level"]
    list_per_page = 20
    ordering = ["sort_order", "-id"]

    readonly_fields = ["created_at", "updated_at", "thumbnail_preview_large"]

    fieldsets = (
        (
            "基础信息",
            {
                "fields": (
                    "project_id",
                    "google_sheet_row_number",
                    "major",
                    "semester",
                )
            },
        ),
        ("项目标题", {"fields": ("project_title_cn", "project_title_en")}),
        ("文案信息", {"fields": ("project_intro", "project_description", "features")}),
        ("人员信息", {"fields": ("students",)}),
        (
            "课程与教师",
            {
                "fields": (
                    ("ib_course", "ib_instructors"),
                    ("fa_course", "fa_instructors"),
                    ("tm_course", "tm_instructors"),
                    ("ge_course", "ge_instructors"),
                    ("cd_course", "cd_instructors"),
                    ("ca_course", "ca_instructors"),
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "媒体资源",
            {
                "fields": (
                    "poster_url",
                    "thumbnail_url",
                    "thumbnail_preview_large",
                    "youtube_url",
                )
            },
        ),
        (
            "文件管理",
            {
                "fields": (
                    "poster_file_id",
                    "poster_file_url",
                    "thumbnail_file_id",
                    "thumbnail_file_url",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "展示控制",
            {
                "fields": (
                    "tags",
                    "is_featured",
                    "is_published",
                    "sort_order",
                    "academic_year",
                    "award_level",
                )
            },
        ),
        (
            "同步信息",
            {
                "fields": ("sync_status",),
                "classes": ("collapse",),
            },
        ),
        (
            "表单提交信息",
            {
                "fields": ("submit_timestamp", "email"),
                "classes": ("collapse",),
            },
        ),
        (
            "后台维护",
            {
                "fields": ("admin_note", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def thumbnail_preview(self, obj):
        if obj.thumbnail_url:
            return format_html(
                '<img src="{}" style="width: 80px; height: 45px; object-fit: cover; border-radius: 4px;" />',
                obj.thumbnail_url,
            )
        return "-"

    thumbnail_preview.short_description = "缩略图"

    def thumbnail_preview_large(self, obj):
        if obj.thumbnail_url:
            return format_html(
                '<img src="{}" style="max-width: 400px; height: auto; border-radius: 8px;" />',
                obj.thumbnail_url,
            )
        return "-"

    thumbnail_preview_large.short_description = "缩略图预览"
