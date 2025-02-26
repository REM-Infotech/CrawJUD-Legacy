import asyncio
import pytest
from unittest import mock
from quart import Quart
from celery import Celery
from socketio import AsyncServer
from crawjud.core import AppFactory
from socketio import ASGIApp
"""Unit tests for the AppFactory class in app/__init__.py."""



@pytest.mark.asyncio
async def test_main(app_factory) -> None:
    """Test the main method of AppFactory."""
    with mock.patch.object(AppFactory, 'create_app', return_value=(mock.Mock(), mock.Mock())) as mock_create_app:
        result = await app_factory.main()
        assert result == mock_create_app.return_value

@pytest.mark.asyncio
async def test_create_app(app_factory) -> None:
    """Test the create_app method of AppFactory."""
    with mock.patch('app.__init__.app') as mock_app, \
         mock.patch('app.__init__.environ', {'AMBIENT_CONFIG': 'development'}), \
         mock.patch('app.__init__.objects_config', {'development': 'app.config.DevelopmentConfig'}), \
         mock.patch('app.__init__.AppFactory.init_extensions', return_value=mock.Mock()), \
         mock.patch('app.__init__.AppFactory.init_routes', return_value=mock.Mock()):

        result = await app_factory.create_app()
        assert isinstance(result, tuple)
        assert isinstance(result[0], ASGIApp)
        assert isinstance(result[1], Celery)


@pytest.mark.asyncio
async def test_start_app(app_factory) -> None:
    """Test the construct_app method of AppFactory."""
    with mock.patch('app.__init__.asyncio.set_event_loop_policy'), \
         mock.patch('app.__init__.asyncio.get_event_loop'), \
         mock.patch.object(AppFactory, 'main', return_value=(mock.Mock(spec=ASGIApp), mock.Mock(spec=Celery))), \
         mock.patch('app.__init__.Thread'):

        result = await app_factory.main()
        assert isinstance(result, tuple)
        assert isinstance(result[0], ASGIApp)
        assert isinstance(result[1], Celery)

def test_starter(app_factory) -> None:
    """Test the starter method of AppFactory."""
    with mock.patch('app.__init__.uvicorn.run') as mock_uvicorn_run:
        mock_app = mock.Mock(spec=Quart)
        app_factory.starter(port=8000, log_output=True, app=mock_app)
        mock_uvicorn_run.assert_called_once_with(mock_app, host="127.0.0.1", port=8000)

def test_handle_exit() -> None:
    """Test the handle_exit method of AppFactory."""
    with mock.patch('app.__init__.sys.exit') as mock_sys_exit:
        AppFactory.handle_exit()
        mock_sys_exit.assert_called_once_with(0)
