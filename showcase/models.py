from django.db import models


class ShowcaseProject(models.Model):
    # 外部同步标识
    project_id = models.CharField(
        max_length=100, unique=True, verbose_name="项目唯一ID"
    )
    sheet_row_id = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Sheet行ID"
    )

    # 基础信息
    program_name = models.CharField(max_length=255, verbose_name="专业名称")
    module_name = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="模块名称"
    )
    course_name = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="课程名称"
    )
    semester = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="学期"
    )

    # 项目标题
    title_zh = models.CharField(max_length=255, verbose_name="项目名称（中文）")
    title_en = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="项目名称（英文）"
    )

    # 文案信息
    background = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="项目背景"
    )
    description = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="作品简介"
    )
    features = models.TextField(blank=True, null=True, verbose_name="作品特色")

    # 人员信息
    students = models.TextField(blank=True, null=True, verbose_name="学生名字")
    teachers = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="指导老师"
    )

    # 媒体资源
    poster_image_url = models.URLField(
        max_length=500, blank=True, null=True, verbose_name="海报图URL"
    )
    thumbnail_image_url = models.URLField(
        max_length=500, blank=True, null=True, verbose_name="封面缩略图URL"
    )
    youtube_url = models.URLField(
        max_length=500, blank=True, null=True, verbose_name="YouTube链接"
    )

    # 扩展展示字段
    tags = models.CharField(max_length=255, blank=True, null=True, verbose_name="标签")
    is_featured = models.BooleanField(default=False, verbose_name="首页推荐")
    is_published = models.BooleanField(default=True, verbose_name="是否发布")
    sort_order = models.IntegerField(default=0, verbose_name="排序值")

    # 同步信息
    sync_source = models.CharField(
        max_length=50, default="google_sheet", verbose_name="同步来源"
    )
    sync_status = models.CharField(
        max_length=50, default="synced", verbose_name="同步状态"
    )
    last_synced_at = models.DateTimeField(
        blank=True, null=True, verbose_name="最后同步时间"
    )

    # 后台维护
    admin_note = models.TextField(blank=True, null=True, verbose_name="后台备注")

    # 审计字段
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "showcase_projects"
        ordering = ["sort_order", "-id"]
        verbose_name = "展示项目"
        verbose_name_plural = "展示项目"

    def __str__(self):
        return f"[{self.project_id}] {self.title_zh}"
