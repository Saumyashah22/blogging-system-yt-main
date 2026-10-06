from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def merge_duplicate_categories(apps, schema_editor):
    Category = apps.get_model('blogs', 'Category')
    Blog = apps.get_model('blogs', 'Blog')
    database = schema_editor.connection.alias
    primary_category_by_name = {}

    categories = list(
        Category.objects.using(database).order_by('pk').values_list(
            'pk',
            'category_name',
        )
    )
    for category_id, category_name in categories:
        primary_category_id = primary_category_by_name.setdefault(
            category_name,
            category_id,
        )
        if primary_category_id == category_id:
            continue

        Blog.objects.using(database).filter(category_id=category_id).update(
            category_id=primary_category_id,
        )
        Category.objects.using(database).filter(pk=category_id).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('blogs', '0005_category_author'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='category',
            name='unique_category_name_per_author',
        ),
        migrations.RunPython(merge_duplicate_categories, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='category',
            name='category_name',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='author',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='categories',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
