"""Main module for the web application."""

if __name__ == "__main__":
    from web import AppFactory

    AppFactory().construct_app()
