from django.apps import AppConfig


class MainConfig(AppConfig):
    name = 'micro'

    def ready(self):
        from micro.dubbo import http_views
        print('我被执行了！')