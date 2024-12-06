# Generated by Django 4.2 on 2024-12-04 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance_managerapp', '0003_transaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='transaction_type',
            field=models.CharField(blank=True, choices=[('income', 'Income'), ('expense', 'Expense')], max_length=7, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='category',
            field=models.CharField(choices=[('salary', 'Salary'), ('freelance', 'Freelance'), ('investment', 'Investment'), ('other', 'Other'), ('rent', 'Rent'), ('groceries', 'Groceries'), ('transport', 'Transport'), ('entertainment', 'Entertainment'), ('other', 'Other')], max_length=50),
        ),
    ]
