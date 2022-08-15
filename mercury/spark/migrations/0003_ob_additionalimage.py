# Generated by Django 4.0.5 on 2022-08-10 09:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import spark.utilities


class Migration(migrations.Migration):

    dependencies = [
        ('spark', '0002_rubric_subrubric_superrubric_rubric_super_rubric'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ob',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=40, verbose_name='Товар')),
                ('content', models.TextField(verbose_name='Описание')),
                ('price', models.FloatField(default=0, verbose_name='Цена')),
                ('contacts', models.TextField(verbose_name='Контакты')),
                ('image', models.ImageField(blank=True, upload_to=spark.utilities.get_timestamp_path, verbose_name='Изображение')),
                ('is_active', models.BooleanField(db_index=True, default=True, verbose_name='Выводить в списке?')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликовано')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Автор объявления')),
                ('rubric', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='spark.subrubric', verbose_name='Рубрика')),
            ],
            options={
                'verbose_name': 'Объявление',
                'verbose_name_plural': 'Объявления',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='AdditionalImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=spark.utilities.get_timestamp_path, verbose_name='Изображение')),
                ('ob', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spark.ob', verbose_name='Объявление')),
            ],
            options={
                'verbose_name': 'Дополнительная иллюстрация',
                'verbose_name_plural': 'Дополнительные иллюстрации',
            },
        ),
    ]