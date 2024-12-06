from django.apps import AppConfig

class FinanceManagerAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'finance_managerapp'

    def ready(self):
        import finance_managerapp.signals
