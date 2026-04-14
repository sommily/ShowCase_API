from rest_framework import serializers
from .models import ShowcaseProject


class ShowcaseProjectListSerializer(serializers.ModelSerializer):
    """项目列表序列化器 - 用于列表展示"""

    features = serializers.SerializerMethodField()
    students = serializers.SerializerMethodField()
    instructors = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    class Meta:
        model = ShowcaseProject
        fields = [
            "id",
            "project_id",
            "major",
            "semester",
            "project_title_cn",
            "project_title_en",
            "project_intro",
            "project_description",
            "features",
            "students",
            "instructors",
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
            "course",
            "poster_url",
            "thumbnail_url",
            "poster_file_id",
            "poster_file_url",
            "thumbnail_file_id",
            "thumbnail_file_url",
            "youtube_url",
            "tags",
            "is_featured",
            "academic_year",
            "award_level",
            "google_sheet_row_number",
            "submit_timestamp",
            "email",
        ]

    def _split_field(self, value):
        """将分隔字符串转为数组，支持 ｜ 和 | 分隔符"""
        if not value:
            return []
        # 支持全角和半角分隔符
        return [
            item.strip() for item in value.replace("｜", "|").split("|") if item.strip()
        ]

    def get_features(self, obj):
        return self._split_field(obj.features)

    def get_students(self, obj):
        return self._split_field(obj.students)

    def get_instructors(self, obj):
        """合并所有教师字段"""
        instructors = []
        for field in [
            obj.ib_instructors,
            obj.fa_instructors,
            obj.tm_instructors,
            obj.ge_instructors,
            obj.cd_instructors,
            obj.ca_instructors,
        ]:
            if field:
                instructors.extend(self._split_field(field))
        return list(set(instructors))  # 去重

    def get_course(self, obj):
        """合并所有课程字段，返回第一个非空课程名"""
        for field in [
            obj.ib_course,
            obj.fa_course,
            obj.tm_course,
            obj.ge_course,
            obj.cd_course,
            obj.ca_course,
        ]:
            if field:
                return field.strip()
        return None

    def get_tags(self, obj):
        return self._split_field(obj.tags)


class ShowcaseProjectDetailSerializer(ShowcaseProjectListSerializer):
    """项目详情序列化器 - 包含更多字段"""

    class Meta(ShowcaseProjectListSerializer.Meta):
        fields = ShowcaseProjectListSerializer.Meta.fields + [
            "sort_order",
            "created_at",
            "updated_at",
        ]


class SyncProjectSerializer(serializers.Serializer):
    """内部同步接口的输入序列化器"""

    project_id = serializers.CharField(max_length=100)
    major = serializers.CharField(max_length=100)
    project_title_cn = serializers.CharField(max_length=255)

    # 可选字段
    google_sheet_row_number = serializers.IntegerField(
        required=False, allow_null=True, default=None
    )
    semester = serializers.CharField(
        max_length=50, required=False, allow_blank=True, default=""
    )
    project_title_en = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    project_intro = serializers.CharField(required=False, allow_blank=True, default="")
    project_description = serializers.CharField(
        required=False, allow_blank=True, default=""
    )
    features = serializers.CharField(required=False, allow_blank=True, default="")
    students = serializers.CharField(required=False, allow_blank=True, default="")
    # 6对课程/教师字段
    ib_course = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    ib_instructors = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    fa_course = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    fa_instructors = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    tm_course = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    tm_instructors = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    ge_course = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    ge_instructors = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    cd_course = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    cd_instructors = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    ca_course = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    ca_instructors = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    poster_url = serializers.CharField(required=False, allow_blank=True, default="")
    thumbnail_url = serializers.CharField(required=False, allow_blank=True, default="")
    youtube_url = serializers.URLField(
        max_length=500, required=False, allow_blank=True, default=""
    )
    tags = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    academic_year = serializers.IntegerField(required=False, default=2025)
    award_level = serializers.IntegerField(
        required=False, allow_null=True, default=None
    )
    # 文件管理字段
    poster_file_id = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    poster_file_url = serializers.CharField(
        required=False, allow_blank=True, default=""
    )
    thumbnail_file_id = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    thumbnail_file_url = serializers.CharField(
        required=False, allow_blank=True, default=""
    )
    # 表单提交信息
    submit_timestamp = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    email = serializers.EmailField(required=False, allow_blank=True, default="")
