"""Main entry point for the Task Manager application."""

if __name__ == "__main__":
    from app import make_celery

    app = make_celery()
