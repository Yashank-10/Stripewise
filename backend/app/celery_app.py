from celery import Celery
from app import create_app

flask_app = create_app()


def make_celery(app):
    celery = Celery(app.import_name)

    celery.conf.update(app.config["CELERY"])

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    # Explicitly import task modules
    celery.conf.imports = (
        "app.tasks.payment_tasks",
    )

    return celery


celery = make_celery(flask_app)

# Force task registration
import app.tasks.payment_tasks
import app.tasks.email_tasks