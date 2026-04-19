import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Gate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Watchlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('phone_number', models.CharField(blank=True, max_length=20)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('reason', models.CharField(max_length=255)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='VisitorPass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visitor_name', models.CharField(max_length=200)),
                ('phone_number', models.CharField(max_length=20)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('id_proof', models.FileField(blank=True, null=True, upload_to='id_proofs/')),
                ('purpose', models.TextField()),
                ('reference_by', models.CharField(blank=True, max_length=200)),
                ('visitor_type', models.CharField(blank=True, default='General', max_length=100)),
                ('valid_from', models.DateTimeField()),
                ('valid_until', models.DateTimeField()),
                ('is_multi_entry', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('checked_in', 'Checked-In'), ('checked_out', 'Checked-Out'), ('expired', 'Expired')], default='pending', max_length=20)),
                ('approval_note', models.CharField(blank=True, max_length=255)),
                ('approved_at', models.DateTimeField(blank=True, null=True)),
                ('qr_token', models.TextField(blank=True)),
                ('qr_image', models.ImageField(blank=True, null=True, upload_to='qr_codes/')),
                ('is_used', models.BooleanField(default=False)),
                ('check_in_at', models.DateTimeField(blank=True, null=True)),
                ('check_out_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_visits', to=settings.AUTH_USER_MODEL)),
                ('check_in_gate', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='checkin_passes', to='visitors.gate')),
                ('check_out_gate', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='checkout_passes', to='visitors.gate')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_visits', to=settings.AUTH_USER_MODEL)),
                ('host', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='hosted_visits', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ScanEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('entry', 'Entry'), ('exit', 'Exit')], max_length=10)),
                ('result', models.CharField(max_length=120)),
                ('scanned_at', models.DateTimeField(auto_now_add=True)),
                ('gate', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='visitors.gate')),
                ('scanned_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='scans', to=settings.AUTH_USER_MODEL)),
                ('visitor_pass', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scan_events', to='visitors.visitorpass')),
            ],
            options={
                'ordering': ['-scanned_at'],
            },
        ),
    ]
