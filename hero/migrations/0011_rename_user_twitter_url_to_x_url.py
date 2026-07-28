from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hero', '0010_user_telegram_url'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='twitter_url',
            new_name='x_url',
        ),
    ]
