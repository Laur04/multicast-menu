ALLOWED_HOSTS = ["*"]
DEBUG=True
SECRET_KEY="secret"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "CONN_MAX_AGE": 20,
        "NAME": "multicast-dev",
        "USER": "user",
        "HOST": "postgres",
        "PORT": 5432,
        "PASSWORD": "password",
    },
}
