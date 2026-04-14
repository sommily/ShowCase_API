"""
DPU Showcase 数据迁移脚本
将 dpu_showcase 表的数据迁移到 showcase_showcaseproject 表
"""

from django.core.management.base import BaseCommand
from django.db import connection, transaction
from showcase.models import ShowcaseProject


class Command(BaseCommand):
    help = "将 dpu_showcase 表的数据迁移到 showcase_showcaseproject 表"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="预览模式：只显示将要迁移的数据，不实际写入",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        if dry_run:
            self.stdout.write(self.style.WARNING("=== 预览模式 (Dry Run) ==="))
        else:
            self.stdout.write(self.style.WARNING("=== 正式执行数据迁移 ==="))

        # 获取源表数据
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM dpu_showcase")
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

        total_source = len(rows)
        self.stdout.write(f"源表 dpu_showcase 数据量: {total_source}")

        # 获取目标表当前数据量
        current_count = ShowcaseProject.objects.count()
        self.stdout.write(
            f"目标表 showcase_showcaseproject 当前数据量: {current_count}"
        )

        if total_source == 0:
            self.stdout.write(self.style.WARNING("源表没有数据，无需迁移"))
            return

        # 字段映射关系
        field_mapping = {
            "semester": "semester",
            "major": "major",
            "project_title_cn": "project_title_cn",
            "project_title_en": "project_title_en",
            "project_description": "project_description",
            "project_intro": "project_intro",
            "students": "students",
            "youtube_url": "youtube_url",
            "email": "email",
            "google_sheet_row_number": "google_sheet_row_number",
            "submit_timestamp": "submit_timestamp",
            "sync_status": "sync_status",
            "created_at": "created_at",
            "updated_at": "updated_at",
            "ib_course": "ib_course",
            "ib_instructors": "ib_instructors",
            "fa_course": "fa_course",
            "fa_instructors": "fa_instructors",
            "tm_course": "tm_course",
            "tm_instructors": "tm_instructors",
            "ge_course": "ge_course",
            "ge_instructors": "ge_instructors",
            "cd_course": "cd_course",
            "cd_instructors": "cd_instructors",
            "ca_course": "ca_course",
            "ca_instructors": "ca_instructors",
            "poster_url": "poster_url",
            "thumbnail_url": "thumbnail_url",
            "poster_file_id": "poster_file_id",
            "poster_file_url": "poster_file_url",
            "thumbnail_file_id": "thumbnail_file_id",
            "thumbnail_file_url": "thumbnail_file_url",
        }

        # 统计
        created_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0

        # 获取已存在的 google_sheet_row_number
        existing_rows = set(
            ShowcaseProject.objects.exclude(
                google_sheet_row_number__isnull=True
            ).values_list("google_sheet_row_number", flat=True)
        )

        self.stdout.write("\n开始迁移数据...")

        for idx, row in enumerate(rows, 1):
            row_data = dict(zip(columns, row))
            source_id = row_data.get("id")
            sheet_row_num = row_data.get("google_sheet_row_number")

            # 构建项目数据
            project_data = {}
            for source_field, target_field in field_mapping.items():
                if source_field in row_data:
                    project_data[target_field] = row_data[source_field]

            # 设置默认值
            project_data["academic_year"] = 2025
            project_data["is_published"] = True
            project_data["is_featured"] = False
            project_data["sort_order"] = 0

            # 生成 project_id
            if sheet_row_num:
                project_data["project_id"] = f"DPU-{sheet_row_num:04d}"
            else:
                project_data["project_id"] = f"DPU-MIGRATED-{source_id:04d}"

            if dry_run:
                # 预览模式
                action = "更新" if sheet_row_num in existing_rows else "创建"
                self.stdout.write(
                    f"[{idx}/{total_source}] {action}: "
                    f"{project_data['project_id']} - "
                    f"{project_data.get('project_title_cn', 'N/A')}"
                )
                if sheet_row_num in existing_rows:
                    updated_count += 1
                else:
                    created_count += 1
                continue

            # 正式迁移
            try:
                with transaction.atomic():
                    if sheet_row_num and sheet_row_num in existing_rows:
                        # 更新已存在的记录
                        ShowcaseProject.objects.filter(
                            google_sheet_row_number=sheet_row_num
                        ).update(**project_data)
                        updated_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"[{idx}/{total_source}] 更新: {project_data['project_id']}"
                            )
                        )
                    else:
                        # 创建新记录
                        ShowcaseProject.objects.create(**project_data)
                        created_count += 1
                        if sheet_row_num:
                            existing_rows.add(sheet_row_num)
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"[{idx}/{total_source}] 创建: {project_data['project_id']}"
                            )
                        )
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"[{idx}/{total_source}] 错误 (id={source_id}): {str(e)}"
                    )
                )

        # 显示结果
        self.stdout.write("\n" + "=" * 50)
        if dry_run:
            self.stdout.write(self.style.WARNING("预览结果 (未实际写入):"))
        else:
            self.stdout.write(self.style.SUCCESS("迁移完成!"))

        self.stdout.write(f"源表数据量: {total_source}")
        self.stdout.write(f"新建记录: {created_count}")
        self.stdout.write(f"更新记录: {updated_count}")
        if skipped_count > 0:
            self.stdout.write(f"跳过记录: {skipped_count}")
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f"错误记录: {error_count}"))

        if not dry_run:
            final_count = ShowcaseProject.objects.count()
            self.stdout.write(f"目标表最终数据量: {final_count}")
