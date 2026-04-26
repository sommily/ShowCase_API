from django.db import models


class ShowcaseProject(models.Model):
    # 外部同步标识
    project_id = models.CharField(
        max_length=100, unique=True, verbose_name="项目唯一ID"
    )
    google_sheet_row_number = models.IntegerField(
        blank=True, null=True, verbose_name="Google Sheet行号"
    )

    # 基础信息
    major = models.CharField(max_length=100, default="", verbose_name="专业名称")
    semester = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="学期"
    )

    # 项目标题
    project_title_cn = models.CharField(
        max_length=255, default="", verbose_name="项目名称（中文）"
    )
    project_title_en = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="项目名称（英文）"
    )

    # 文案信息
    project_intro = models.TextField(blank=True, null=True, verbose_name="项目背景")
    project_description = models.TextField(
        blank=True, null=True, verbose_name="作品简介"
    )
    features = models.TextField(blank=True, null=True, verbose_name="作品特色")

    # 人员信息
    students = models.TextField(blank=True, null=True, verbose_name="学生名字")

    # 6对课程/教师字段
    ib_course = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="IB课程"
    )
    ib_instructors = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="IB教师"
    )
    fa_course = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="FA课程"
    )
    fa_instructors = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="FA教师"
    )
    tm_course = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="TM课程"
    )
    tm_instructors = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="TM教师"
    )
    ge_course = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="GE课程"
    )
    ge_instructors = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="GE教师"
    )
    cd_course = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="CD课程"
    )
    cd_instructors = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="CD教师"
    )
    ca_course = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="CA课程"
    )
    ca_instructors = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="CA教师"
    )

    # 媒体资源
    poster_url = models.TextField(blank=True, null=True, verbose_name="海报图URL")
    thumbnail_url = models.TextField(
        blank=True, null=True, verbose_name="封面缩略图URL"
    )
    youtube_url = models.URLField(
        max_length=500, blank=True, null=True, verbose_name="YouTube链接"
    )

    # 文件管理字段
    poster_file_id = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="海报文件ID"
    )
    poster_file_url = models.TextField(
        blank=True, null=True, verbose_name="海报文件URL"
    )
    thumbnail_file_id = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="缩略图文件ID"
    )
    thumbnail_file_url = models.TextField(
        blank=True, null=True, verbose_name="缩略图文件URL"
    )

    # 扩展展示字段
    tags = models.CharField(max_length=255, blank=True, null=True, verbose_name="标签")
    is_featured = models.BooleanField(default=False, verbose_name="首页推荐")
    is_published = models.BooleanField(default=True, verbose_name="是否发布")
    sort_order = models.IntegerField(default=0, verbose_name="排序值")

    # 评选活动
    academic_year = models.IntegerField(default=2025, verbose_name="评选学年")
    award_level = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="奖项等级",
        choices=[
            (1, "一等奖"),
            (2, "二等奖"),
            (3, "三等奖"),
            (4, "优秀奖"),
        ],
    )

    # 同步信息
    sync_status = models.CharField(
        max_length=50, default="synced", verbose_name="同步状态"
    )

    # 后台维护
    admin_note = models.TextField(blank=True, null=True, verbose_name="后台备注")

    # 表单提交信息
    submit_timestamp = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="提交时间"
    )
    email = models.EmailField(blank=True, null=True, verbose_name="联系邮箱")

    # 互动数据
    view_count = models.PositiveIntegerField(default=0, verbose_name="浏览量")
    like_count = models.PositiveIntegerField(default=0, verbose_name="点赞数")

    # 审计字段
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "showcase_projects"
        ordering = ["-academic_year", "sort_order", "-id"]
        verbose_name = "展示项目"
        verbose_name_plural = "展示项目"

    def __str__(self):
        return self.project_title_cn or self.project_title_en or f"Project {self.id}"
