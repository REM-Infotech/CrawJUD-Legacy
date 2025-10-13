"""App entry point."""

if __name__ == "__main__":
    import asyncio

    from app import main_app

    app = asyncio.run(main_app())

    app.run(port=5000)
