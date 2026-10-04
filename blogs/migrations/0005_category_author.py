from collections import defaultdict

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def assign_category_authors(apps, schema_editor):
    Category = apps.get_model('blogs', 'Category')
    Blog = apps.get_model('blogs', 'Blog')
    database = schema_editor.connection.alias

    categories = list(
        Category.objects.using(database)
        .order_by('pk')
        .values_list('pk', 'category_name')
    )
    for category_id, category_name in categories:
        blogs_by_author = defaultdict(list)
        blog_authors = (
            Blog.objects.using(database)
            .filter(category_id=category_id)
            .order_by('author_id')
            .values_list('pk', 'author_id')
        )
        for blog_id, author_id in blog_authors:
            blogs_by_author[author_id].append(blog_id)

        if not blogs_by_author:
            continue

        author_groups = sorted(blogs_by_author.items())
        Category.objects.using(database).filter(pk=category_id).update(
            author_id=author_groups[0][0]
        )

        for author_id, blog_ids in author_groups[1:]:
            copied_category = Category.objects.using(database).create(
                category_name=category_name,
                author_id=author_id,
            )
            Blog.objects.using(database).filter(pk__in=blog_ids).update(
                category_id=copied_category.pk
            )


def remove_category_authors(apps, schema_editor):
    Category = apps.get_model('blogs', 'Category')
    Blog = apps.get_model('blogs', 'Blog')
    database = schema_editor.connection.alias
    category_names = list(
        Category.objects.using(database)
        .order_by()
        .values_list('category_name', flat=True)
        .distinct()
    )

    for category_name in category_names:
        category_ids = list(
            Category.objects.using(database)
            .filter(category_name=category_name)
            .order_by('pk')
            .values_list('pk', flat=True)
        )
        primary_category_id = category_ids[0]
        Blog.objects.using(database).filter(
            category_id__in=category_ids[1:]
        ).update(category_id=primary_category_id)
        Category.objects.using(database).filter(
            pk__in=category_ids[1:]
        ).delete()
        Category.objects.using(database).filter(
            pk=primary_category_id
        ).update(author_id=None)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blogs', '0004_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='author',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='categories',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='category',
            name='category_name',
            field=models.CharField(max_length=50),
        ),
        migrations.RunPython(assign_category_authors, remove_category_authors),
        migrations.AddConstraint(
            model_name='category',
            constraint=models.UniqueConstraint(
                fields=('author', 'category_name'),
                name='unique_category_name_per_author',
            ),
        ),
    ]
