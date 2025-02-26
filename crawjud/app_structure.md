# App Structure Documentation

This document details the structure and components of the `app` directory in the CrawJUD-Bots project.

Portuguese (Br) version available [here](./doc/estrutura_app.md).

## Core Components

### `__init__.py`
Contains the `AppFactory` class responsible for:
- Application initialization
- Configuration loading
- Server startup management
- Extension and route registration

### `asgi.py`
ASGI application entry point that:
- Sets environment variables for production
- Initializes the Quart application
- Serves as the main server startup file

### `beat.py`
Celery beat scheduler that:
- Manages periodic tasks
- Configures logging for scheduled jobs
- Uses a custom database scheduler

### `worker.py`
Celery worker implementation that:
- Handles task processing
- Manages concurrency settings
- Configures worker logging

## Core Directory (`core/`)

### `configurator.py`
Configuration management module that:
- Loads environment-specific settings
- Initializes application extensions
- Sets up logging and database connections

### `extensions.py`
Extension initialization module that:
- Sets up Flask-Mail
- Configures Talisman security
- Initializes SQLAlchemy
- Sets up other Flask/Quart extensions

### `routing.py`
Route registration module that:
- Registers API endpoints
- Sets up WebSocket routes
- Manages URL patterns

## Models Directory (`models/`)
Contains SQLAlchemy models for:
- User management
- Task scheduling
- System configuration
- Data persistence

## Routes Directory (`routes/`)
Contains route handlers for:
- API endpoints
- WebSocket connections
- System operations
- Task management

## Forms Directory (`Forms/`)
Contains form validators and processors for:
- Data input validation
- Request processing
- Form rendering

## Environment Configuration
The application supports multiple environments:
- Development
- Production
- Testing

Each environment has its specific configuration class in `config.py`.
