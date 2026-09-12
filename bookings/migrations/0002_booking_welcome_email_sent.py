# Generated migration for welcome_email_sent field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='welcome_email_sent',
            field=models.BooleanField(default=False),
        ),
        migrations.AddIndex(
            model_name='booking',
            index=models.Index(fields=['check_in', 'welcome_email_sent'], name='booking_checkin_email_idx'),
        ),
    ]