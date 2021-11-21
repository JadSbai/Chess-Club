from django.apps import AppConfig



class ChessClubsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chessclubs'

    def ready(self):
        from .groups import set_up_app_groups
        set_up_app_groups()
