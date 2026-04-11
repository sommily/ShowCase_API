from django.contrib import admin
from django.utils.html import format_html
from .models import ShowcaseProject


@admin.register(ShowcaseProject)
class ShowcaseProjectAdmin(admin.ModelAdmin):
    list_display = [
        "thumbnail_preview",
        "title_zh",
        "program_name",
        "module_name",
        "semester",
        "is_published",
        "is_featured",
        "sort_order",
        "last_synced_at",
    ]
    list_filter = [
        "program_name",
        "module_name",
        "semester",
        "is_published",
        "is_featured",
    ]
    search_fields = ["project_id", "title_zh", "title_en", "students", "teachers"]
    list_editable = ["is_published", "is_featured", "sort_order"]
    list_per_page = 20
    ordering = ["sort_order", "-id"]

    readonly_fields = ["created_at", "updated_at", "thumbnail_preview_large"]

    fieldsets = (
        (
            "基础信息",
            {
                "fields": (
                    "project_id",
                    "sheet_row_id",
                    "program_name",
                    "module_name",
                    "course_name",
                    "semester",
                )
            },
        ),
        ("项目标题", {"fields": ("title_zh", "title_en")}),
        ("文案信息", {"fields": ("background", "description", "features")}),
        ("人员信息", {"fields": ("students", "teachers")}),
        (
            "媒体资源",
            {
                "fields": (
                    "poster_image_url",
                    "thumbnail_image_url",
                    "thumbnail_preview_large",
                    "youtube_url",
                )
            },
        ),
        ("展示控制", {"fields": ("tags", "is_featured", "is_published", "sort_order")}),
        (
            "同步信息",
            {
                "fields": ("sync_source", "sync_status", "last_synced_at"),
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
        if obj.thumbnail_image_url:
            return format_html(
                '<img src="{}" style="width: 80px; height: 45px; object-fit: cover; border-radius: 4px;" />',
                obj.thumbnail_image_url,
            )
        return "-"

    thumbnail_preview.short_description = "缩略图"

    def thumbnail_preview_large(self, obj):
        if obj.thumbnail_image_url:
            return format_html(
                '<img src="{}" style="max-width: 400px; height: auto; border-radius: 8px;" />',
                obj.thumbnail_image_url,
            )
        return "-"

    thumbnail_preview_large.short_description = "缩略图预览"
