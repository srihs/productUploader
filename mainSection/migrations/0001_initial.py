# Generated by Django 2.1.3 on 2019-01-20 02:09

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('is_buyer', models.BooleanField(default=False)),
                ('is_officeUser', models.BooleanField(default=False)),
                ('is_storeUser', models.BooleanField(default=False)),
                ('productCode', models.CharField(max_length=50)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('shippingPoint', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name_plural': 'ShippingPoints',
            },
        ),
        migrations.CreateModel(
            name='Products',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('sku', models.CharField(max_length=100)),
                ('vendor', models.CharField(blank=True, max_length=500)),
                ('weight', models.PositiveIntegerField()),
                ('sellingPrice', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('productImg', models.ImageField(blank=True, max_length=5000, null=True, upload_to='images/%Y/%m/%d/')),
                ('archived', models.BooleanField(default='False')),
                ('dateCreated', models.DateTimeField(default=django.utils.timezone.now)),
                ('userCreated', models.CharField(max_length=500)),
                ('dateModified', models.DateTimeField(default=django.utils.timezone.now)),
                ('userModified', models.CharField(max_length=500)),
            ],
            options={
                'verbose_name_plural': 'Products',
            },
        ),
        migrations.CreateModel(
            name='ProductTypes',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('productType', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name_plural': 'ProductTypes',
            },
        ),
        migrations.CreateModel(
            name='Shipment',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('shipmentNumber', models.CharField(max_length=50)),
                ('shipmentDate', models.DateField()),
                ('isClosed', models.BooleanField(default='False')),
                ('isFinalized', models.BooleanField(default='False')),
                ('isCostapplied', models.BooleanField(default='False')),
                ('isCostbaseFinalized', models.BooleanField(default='False')),
                ('costBase', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('costFile', models.FileField(blank=True, max_length=5000, null=True, upload_to='Costing/%Y/%m/%d/')),
                ('dateCreated', models.DateTimeField(default=django.utils.timezone.now)),
                ('userCreated', models.CharField(max_length=500)),
                ('dateModified', models.DateTimeField(default=django.utils.timezone.now)),
                ('userModified', models.CharField(max_length=500)),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('shippingPoint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainSection.Country')),
            ],
        ),
        migrations.CreateModel(
            name='ShipmentDetail',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('indPrice', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('qty', models.PositiveIntegerField(blank=True, null=True)),
                ('receivedQty', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('weight', models.PositiveIntegerField()),
                ('costBase', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('sellingPrice', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('billDate', models.DateField(default=django.utils.timezone.now)),
                ('billNumber', models.PositiveIntegerField(blank=True, null=True)),
                ('is_checked', models.BooleanField(default='False')),
                ('is_completeReceive', models.BooleanField(default='False')),
                ('is_grn', models.BooleanField(default='False')),
                ('archived', models.BooleanField(default='False')),
                ('dateCreated', models.DateTimeField(default=django.utils.timezone.now)),
                ('userCreated', models.CharField(max_length=500)),
                ('dateModified', models.DateTimeField(default=django.utils.timezone.now)),
                ('userModified', models.CharField(max_length=500)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainSection.Products')),
                ('shipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainSection.Shipment')),
            ],
            options={
                'verbose_name_plural': 'ShipmentDetails',
            },
        ),
        migrations.AddField(
            model_name='products',
            name='types',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainSection.ProductTypes'),
        ),
    ]
