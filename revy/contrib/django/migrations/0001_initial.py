from django.conf import settings
import django.core.serializers.json
from django.db import migrations, models
import django.db.models.deletion
import revy.abc.attribute_delta
import revy.abc.delta
import revy.abc.object_delta
import revy.abc.revision


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Delta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('actor_id', models.TextField(blank=True, db_index=True, default=None, null=True, verbose_name='actor ID')),
                ('action', models.CharField(choices=[('Create', 'Create'), ('Update', 'Update'), ('Delete', 'Delete'), ('Set', 'Set'), ('Unset', 'Unset')], db_index=True, max_length=6, verbose_name='action')),
                ('description', models.TextField(blank=True, default='', verbose_name='description')),
                ('content_id', models.TextField(blank=True, db_index=True, default=None, null=True, verbose_name='content ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True, verbose_name='updated at')),
                ('actor_type', models.ForeignKey(blank=True, db_column='actor_type_id', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='deltas_created_by', related_query_name='delta_created_by', to='contenttypes.contenttype', verbose_name='actor type')),
                ('content_type', models.ForeignKey(blank=True, db_column='content_type_id', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='deltas', related_query_name='delta', to='contenttypes.contenttype', verbose_name='content type')),
            ],
            options={
                'verbose_name': 'delta',
                'verbose_name_plural': 'deltas',
                'db_table': 'revy__deltas',
                'swappable': 'REVY_DELTA_MODEL',
            },
            bases=(revy.abc.delta.Delta, models.Model),
        ),
        migrations.CreateModel(
            name='Revision',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, default='', verbose_name='description')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True, verbose_name='updated at')),
            ],
            options={
                'verbose_name': 'revision',
                'verbose_name_plural': 'revisions',
                'db_table': 'revy__revisions',
                'swappable': 'REVY_REVISION_MODEL',
            },
            bases=(revy.abc.revision.Revision, models.Model),
        ),
        migrations.CreateModel(
            name='ObjectDelta',
            fields=[
                ('object_delta_ptr', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='object_delta', related_query_name='object_delta', serialize=False, to=settings.REVY_DELTA_MODEL, verbose_name='object delta pointer')),
            ],
            options={
                'verbose_name': 'object delta',
                'verbose_name_plural': 'object deltas',
                'db_table': 'revy__object_deltas',
                'swappable': 'REVY_OBJECT_DELTA_MODEL',
            },
            bases=(revy.abc.object_delta.ObjectDelta, 'revy.delta', revy.abc.delta.Delta, models.Model),
        ),
        migrations.AddField(
            model_name='delta',
            name='revision',
            field=models.ForeignKey(db_column='revision_id', on_delete=django.db.models.deletion.CASCADE, related_name='deltas', related_query_name='delta', to=settings.REVY_REVISION_MODEL, verbose_name='revision'),
        ),
        migrations.CreateModel(
            name='AttributeDelta',
            fields=[
                ('field_name', models.TextField(db_index=True, verbose_name='field name')),
                ('old_value', models.JSONField(blank=True, default=None, encoder=django.core.serializers.json.DjangoJSONEncoder, null=True, verbose_name='old value')),
                ('new_value', models.JSONField(blank=True, default=None, encoder=django.core.serializers.json.DjangoJSONEncoder, null=True, verbose_name='new value')),
                ('attribute_delta_ptr', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='attribute_delta', related_query_name='attribute_delta', serialize=False, to=settings.REVY_DELTA_MODEL, verbose_name='attribute delta')),
                ('parent', models.ForeignKey(db_column='parent_id', on_delete=django.db.models.deletion.CASCADE, related_name='children', related_query_name='child', to=settings.REVY_OBJECT_DELTA_MODEL, verbose_name='parent')),
            ],
            options={
                'verbose_name': 'attribute delta',
                'verbose_name_plural': 'attribute deltas',
                'db_table': 'revy__attribute_deltas',
                'swappable': 'REVY_ATTRIBUTE_DELTA_MODEL',
            },
            bases=(revy.abc.attribute_delta.AttributeDelta, 'revy.delta', revy.abc.delta.Delta, models.Model),
        ),
    ]
