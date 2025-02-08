"""module used to import the app module to the routes package."""

if __name__ == "__main__":
    from app import AppFactory

    AppFactory.beat_app()
