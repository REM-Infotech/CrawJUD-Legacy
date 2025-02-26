"""Crawjud bots package main entry point."""


def main() -> None:
    """Run the server application."""
    from server.main import main_server

    main_server()


if __name__ == "__main__":
    main()
