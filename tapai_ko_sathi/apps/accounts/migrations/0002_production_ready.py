"""
Migration: Production-Ready Models
- Extended User Model with phone, email verification, tracking
- UserProfile and Address models
- Enhanced Cart with session-to-user merging
- Complete Payment model with transaction tracking
- Comprehensive Order model with inventory management
"""
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        # Update User model
        migrations.AddField(
            model_name='user',
            name='phone_number',
            field=models.CharField(
                blank=True, 
                max_length=17,
                null=True, 
                unique=True,
                validators=[django.core.validators.RegexValidator(
                    message='Phone number must be entered in the format: +999999999. Up to 15 digits allowed.',
                    regex='^\\+?1?\\d{9,15}$'
                )]
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='email_verified_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='last_login_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['email'], name='email_idx'),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['is_email_verified'], name='email_verified_idx'),
        ),
        
        # Create UserProfile model
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_image', models.ImageField(blank=True, null=True, upload_to='profiles/')),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other'), ('N', 'Prefer not to say')], max_length=1)),
                ('bio', models.TextField(blank=True, max_length=500)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to='accounts.user')),
            ],
        ),
        
        # Create Address model
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address_type', models.CharField(choices=[('home', 'Home'), ('work', 'Work'), ('other', 'Other')], default='home', max_length=20)),
                ('full_name', models.CharField(max_length=150)),
                ('phone_number', models.CharField(max_length=17)),
                ('street_address', models.CharField(max_length=255)),
                ('apartment_address', models.CharField(blank=True, max_length=255)),
                ('city', models.CharField(max_length=80)),
                ('state', models.CharField(blank=True, max_length=80)),
                ('country', models.CharField(max_length=80)),
                ('postal_code', models.CharField(max_length=20)),
                ('is_default', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to='accounts.user')),
            ],
            options={
                'verbose_name_plural': 'Addresses',
            },
        ),
        migrations.AddIndex(
            model_name='address',
            index=models.Index(fields=['user', 'is_default'], name='user_default_idx'),
        ),
        
        # Update default_address field in UserProfile
        migrations.AddField(
            model_name='userprofile',
            name='default_address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_default', to='accounts.address'),
        ),
    ]
