from rest_framework import serializers
from .models import ShowcaseProject


class ShowcaseProjectListSerializer(serializers.ModelSerializer):
    """项目列表序列化器 - 用于列表展示"""

    features = serializers.SerializerMethodField()
    students = serializers.SerializerMethodField()
    teachers = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    class Meta:
        model = ShowcaseProject
        fields = [
            "id",
            "project_id",
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
            "is_featured",
            "academic_year",
            "award_level",
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

    def get_teachers(self, obj):
        return self._split_field(obj.teachers)

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
    program_name = serializers.CharField(max_length=255)
    title_zh = serializers.CharField(max_length=255)

    # 可选字段
    sheet_row_id = serializers.CharField(
        max_length=100, required=False, allow_blank=True, default=""
    )
    module_name = serializers.CharField(
        max_length=100, required=False, allow_blank=True, default=""
    )
    course_name = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    semester = serializers.CharField(
        max_length=50, required=False, allow_blank=True, default=""
    )
    title_en = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    background = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    description = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    features = serializers.CharField(required=False, allow_blank=True, default="")
    students = serializers.CharField(required=False, allow_blank=True, default="")
    teachers = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    poster_image_url = serializers.URLField(
        max_length=500, required=False, allow_blank=True, default=""
    )
    thumbnail_image_url = serializers.URLField(
        max_length=500, required=False, allow_blank=True, default=""
    )
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
