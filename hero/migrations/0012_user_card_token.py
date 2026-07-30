import uuid

from django.db import migrations, models


def populate_card_tokens(apps, schema_editor):
    User = apps.get_model('hero', 'User')
    for user in User.objects.filter(card_token__isnull=True).iterator():
        user.card_token = uuid.uuid4()
        user.save(update_fields=['card_token'])


class Migration(migrations.Migration):

    dependencies = [
        ('hero', '0011_rename_user_twitter_url_to_x_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='card_token',
            field=models.UUIDField(null=True, editable=False),
        ),
        migrations.RunPython(populate_card_tokens, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='user',
            name='card_token',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
