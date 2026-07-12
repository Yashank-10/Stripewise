from app.celery_app import celery


@celery.task
def test_task():
    print("=" * 50)
    print("CELERY TASK EXECUTED SUCCESSFULLY")
    print("=" * 50)

    return "success"