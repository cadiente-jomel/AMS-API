# Generated by Django 4.1.1 on 2022-10-24 10:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("buildings", "0004_room_rent_price_tenantroom_start_date"),
        ("faqs", "0002_alter_answer_answered_by"),
    ]

    operations = [
        migrations.AddField(
            model_name="concern",
            name="branch",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="branch_concern",
                to="buildings.branch",
            ),
        ),
    ]
