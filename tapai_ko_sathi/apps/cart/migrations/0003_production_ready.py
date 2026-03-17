"""
Migration: Production-Ready Cart System
- Convert user relation from ForeignKey to OneToOneField
- Support session-based and user-based carts
- Add session_key nullable field
"""
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0002_cart_cart_cart_updated_c46eb6_idx'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='user',
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='cart',
                to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AlterField(
            model_name='cart',
            name='session_key',
            field=models.CharField(blank=True, db_index=True, max_length=40, null=True),
        ),
        migrations.AddIndex(
            model_name='cart',
            index=models.Index(fields=['user'], name='cart_user_idx'),
        ),
    ]
