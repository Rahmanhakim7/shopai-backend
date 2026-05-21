from django.db import migrations, models
class Migration(migrations.Migration):
    dependencies = [
        ('products', '0002_product_seller'),
    ]
    operations = [
        migrations.AddField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='products/'),
        ),
        migrations.AddField(
            model_name='product',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive'), ('sold_out', 'Sold Out')], default='active', max_length=20),
        ),
        migrations.AddField(
            model_name='product',
            name='stock',
            field=models.PositiveBigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='product',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
