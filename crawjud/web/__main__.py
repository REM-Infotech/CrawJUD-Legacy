"""Main module for the web application."""

if __name__ == "__main__":
    from crawjud.web import AppFactory

    AppFactory().construct_app()
