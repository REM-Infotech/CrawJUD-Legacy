import asyncio
import pytest
from unittest import mock
from quart import Quart
from celery import Celery
from socketio import ASGIApp, AsyncServer
from app import AppFactory

"""Tests for the CrawJUD-Bots app initialization module."""


@pytest.mark.asyncio
async def test_main() -> None:
    """Test the main method of AppFactory."""
    factory = AppFactory()
    result = await factory.main()
    assert isinstance(result, tuple)
    assert isinstance(result[0], ASGIApp)
    assert isinstance(result[1], Celery)

@pytest.mark.asyncio
async def test_create_app() -> None:
    """Test the create_app method of AppFactory."""
    factory = AppFactory()
    result = await factory.create_app()
    assert isinstance(result, tuple)
    assert isinstance(result[0], ASGIApp)
    assert isinstance(result[1], Celery)

@pytest.mark.asyncio
async def test_init_routes() -> None:
    """Test the init_routes method of AppFactory."""
    factory = AppFactory()
    app = Quart(__name__)
    await factory.init_routes(app)
    assert 'routes' in app.blueprints

@pytest.mark.asyncio
async def test_init_extensions() -> None:
    """Test the init_extensions method of AppFactory."""
    factory = AppFactory()
    app = Quart(__name__)
    result = await factory.init_extensions(app)
    assert isinstance(result, AsyncServer)

def test_start_app() -> None:
    """Test the start_app method of AppFactory."""
    with mock.patch('asyncio.get_event_loop', return_value=mock.Mock()):
        app, celery = AppFactory.start_app()
        assert isinstance(app, Quart)
        assert isinstance(celery, Celery)

def test_starter() -> None:
    """Test the starter method of AppFactory."""
    with mock.patch('uvicorn.run') as mock_run:
        AppFactory.starter(port=8000, log_output=True, app=Quart(__name__))
        mock_run.assert_called_once()

def test_handle_exit() -> None:
    """Test the handle_exit method of AppFactory."""
    with mock.patch('sys.exit') as mock_exit:
        AppFactory.handle_exit()
        mock_exit.assert_called_once()
