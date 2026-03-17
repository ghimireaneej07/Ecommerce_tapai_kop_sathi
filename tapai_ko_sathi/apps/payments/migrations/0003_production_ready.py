"""
Migration: Production-Ready Payment System
- Add comprehensive payment verification fields
- Add payment lifecycle tracking
- Create PaymentLog audit table
- Add secure transaction ID tracking
"""
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_alter_payment_gateway'),
    ]

    operations = [
        # Update Payment model
        migrations.AddField(
            model_name='payment',
            name='payment_method',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='payment',
            name='payment_signature',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='payment',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='payment',
            name='error_message',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='initiated_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='verified_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='paid_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        
        # Rename updated_at to avoid conflicts
        migrations.AlterField(
            model_name='payment',
            name='transaction_id',
            field=models.CharField(blank=True, db_index=True, max_length=100, unique=True),
        ),
        
        # Update status choices
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(
                choices=[
                    ('initiated', 'Initiated'),
                    ('pending', 'Pending'),
                    ('authorized', 'Authorized'),
                    ('captured', 'Captured'),
                    ('success', 'Success'),
                    ('failed', 'Failed'),
                    ('cancelled', 'Cancelled'),
                    ('refunded', 'Refunded'),
                ],
                db_index=True,
                default='initiated',
                max_length=20
            ),
        ),
        
        # Add indexes
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['gateway', 'transaction_id'], name='gateway_txn_idx'),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['status'], name='status_idx'),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['paid_at'], name='paid_at_idx'),
        ),
        
        # Create PaymentLog model
        migrations.CreateModel(
            name='PaymentLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=20)),
                ('message', models.TextField()),
                ('metadata', models.JSONField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('payment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='payments.payment')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        
        migrations.AddIndex(
            model_name='paymentlog',
            index=models.Index(fields=['payment', 'created_at'], name='payment_log_idx'),
        ),
    ]
