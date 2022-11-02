# local files imports
from .base import *
from colorama import init, Fore, Style

init()

DEBUG = True


ALLOWED_HOSTS = ["ams-api-production.up.railway", "ams-api-production.up.railway.app", "localhost"]


INSTALLED_APPS += ["debug_toolbar"]


MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


INTERNAL_IPS = ["127.0.0.1"]


DEBUG_TOOLBAR_PANELS = [
    "debug_toolbar.panels.history.HistoryPanel",
    "debug_toolbar.panels.versions.VersionsPanel",
    "debug_toolbar.panels.timer.TimerPanel",
    "debug_toolbar.panels.settings.SettingsPanel",
    "debug_toolbar.panels.headers.HeadersPanel",
    "debug_toolbar.panels.request.RequestPanel",
    "debug_toolbar.panels.sql.SQLPanel",
    "debug_toolbar.panels.staticfiles.StaticFilesPanel",
    "debug_toolbar.panels.templates.TemplatesPanel",
    "debug_toolbar.panels.cache.CachePanel",
    "debug_toolbar.panels.signals.SignalsPanel",
    "debug_toolbar.panels.logging.LoggingPanel",
    "debug_toolbar.panels.redirects.RedirectsPanel",
    "debug_toolbar.panels.profiling.ProfilingPanel",
]


def show_toolbar(request):
    return True


DEBUG_TOOLBAR_CONFIG = {
    "INTERCEPTS_REDIRECTS": False,
    "SHOW_TOOLBAR_CALLBACK": show_toolbar,
}


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "%(levelname)s - %(asctime)s - %(module)s : %(message)s"},
        "simple": {
            "format": f"[{Fore.GREEN}%(levelname)s]{Style.RESET_ALL} %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "level": "INFO",
        },
        # "file": {
        #     "class": "logging.FileHandler",
        #     "filename": "logs/debug.log",
        #     "formatter": "verbose",
        #     "level": "WARNING",
        # },
    },
    "loggers": {
        "main": {
            "handlers": ["console"],
            "propagate": True,
            "level": "INFO",
        },
        "secondary": {
            "handlers": ["console"],
            "propagate": True,
            "level": "INFO",
        },
    },
}


MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
