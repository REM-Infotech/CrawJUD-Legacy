# Decorators - Decoradores Python Customizados

Este módulo contém decoradores Python personalizados utilizados para funcionalidades transversais como autenticação, logging, cache, validação e controle de CORS na aplicação CrawJUD.

## Tipos de Decoradores

### API Decorators

Decoradores específicos para endpoints da API web.

### Authentication Decorators

Decoradores para autenticação e autorização.

### Caching Decorators

Decoradores para cache de resultados.

### Logging Decorators

Decoradores para logging automático.

### Validation Decorators

Decoradores para validação de dados.

## Decoradores Principais

### CORS Decorator (`api.py`)

#### @CrossDomain

```python
def CrossDomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True, automatic_options=True):
    """Decorador para habilitar CORS em endpoints da API.

    Args:
        origin (str|list): Origens permitidas
        methods (list): Métodos HTTP permitidos
        headers (list): Headers permitidos
        max_age (int): Tempo de cache preflight
        attach_to_all (bool): Aplicar a todas as rotas
        automatic_options (bool): Responder automaticamente a OPTIONS

    Returns:
        function: Decorador configurado

    Example:
        @app.route('/api/endpoint')
        @CrossDomain(origin='*', methods=['GET', 'POST'])
        def endpoint():
            return {"status": "ok"}
    """
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, str):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, str):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods
        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers
            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp
        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator
```

### Authentication Decorators

#### @jwt_required_custom

```python
def jwt_required_custom(optional=False, verify_type=True):
    """Decorador customizado para autenticação JWT.

    Args:
        optional (bool): Se True, token é opcional
        verify_type (bool): Verificar tipo do token

    Returns:
        function: Decorador de autenticação

    Example:
        @app.route('/protected')
        @jwt_required_custom()
        def protected_endpoint():
            user_id = get_jwt_identity()
            return {"user_id": user_id}
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                # Verificar token JWT
                token = get_jwt()
                if not token and not optional:
                    raise AuthenticationError("Token obrigatório")

                # Verificar se token está na blacklist
                if token and is_token_revoked(token):
                    raise AuthenticationError("Token revogado")

                # Verificar expiração
                if token and is_token_expired(token):
                    raise AuthenticationError("Token expirado")

                return func(*args, **kwargs)

            except JWTError as e:
                if optional:
                    return func(*args, **kwargs)
                raise AuthenticationError(f"Token inválido: {e}")

        return wrapper
    return decorator
```

#### @require_permissions

```python
def require_permissions(*required_permissions):
    """Decorador para verificar permissões específicas.

    Args:
        *required_permissions: Lista de permissões necessárias

    Returns:
        function: Decorador de autorização

    Example:
        @app.route('/admin/users')
        @jwt_required_custom()
        @require_permissions('admin', 'user_management')
        def admin_users():
            return {"users": []}
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user_permissions = get_user_permissions(user_id)

            for permission in required_permissions:
                if permission not in user_permissions:
                    raise PermissionError(f"Permissão '{permission}' necessária")

            return func(*args, **kwargs)
        return wrapper
    return decorator
```

### Logging Decorators

#### @log_execution

```python
def log_execution(level='INFO', include_args=False, include_result=False):
    """Decorador para logging automático de execução.

    Args:
        level (str): Nível do log
        include_args (bool): Incluir argumentos no log
        include_result (bool): Incluir resultado no log

    Returns:
        function: Decorador de logging

    Example:
        @log_execution(level='DEBUG', include_args=True)
        def important_function(param1, param2):
            return {"result": "success"}
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)

            start_time = time.time()
            func_name = func.__qualname__

            # Log de início
            log_msg = f"Executando {func_name}"
            if include_args:
                log_msg += f" com args={args}, kwargs={kwargs}"

            logger.log(getattr(logging, level), log_msg)

            try:
                result = func(*args, **kwargs)

                # Log de sucesso
                duration = time.time() - start_time
                success_msg = f"{func_name} executado com sucesso em {duration:.2f}s"
                if include_result:
                    success_msg += f" - resultado: {result}"

                logger.log(getattr(logging, level), success_msg)

                return result

            except Exception as e:
                # Log de erro
                duration = time.time() - start_time
                error_msg = f"{func_name} falhou após {duration:.2f}s - erro: {e}"
                logger.error(error_msg, exc_info=True)
                raise

        return wrapper
    return decorator
```

#### @audit_log

```python
def audit_log(action, resource_type):
    """Decorador para log de auditoria.

    Args:
        action (str): Ação sendo executada
        resource_type (str): Tipo de recurso

    Returns:
        function: Decorador de auditoria

    Example:
        @audit_log('CREATE', 'USER')
        def create_user(user_data):
            return new_user
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity() if has_request_context() else None

            try:
                result = func(*args, **kwargs)

                # Log de auditoria para sucesso
                create_audit_log({
                    'user_id': user_id,
                    'action': action,
                    'resource_type': resource_type,
                    'status': 'SUCCESS',
                    'timestamp': datetime.now(),
                    'details': {'args': args, 'kwargs': kwargs}
                })

                return result

            except Exception as e:
                # Log de auditoria para erro
                create_audit_log({
                    'user_id': user_id,
                    'action': action,
                    'resource_type': resource_type,
                    'status': 'ERROR',
                    'error': str(e),
                    'timestamp': datetime.now()
                })
                raise

        return wrapper
    return decorator
```

### Caching Decorators

#### @cache_result

```python
def cache_result(ttl=300, key_prefix=None, cache_backend='redis'):
    """Decorador para cache de resultados.

    Args:
        ttl (int): Time to live em segundos
        key_prefix (str): Prefixo da chave de cache
        cache_backend (str): Backend de cache

    Returns:
        function: Decorador de cache

    Example:
        @cache_result(ttl=600, key_prefix='user_data')
        def get_user_data(user_id):
            return expensive_database_query(user_id)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Gerar chave de cache
            cache_key = generate_cache_key(func, args, kwargs, key_prefix)

            # Tentar obter do cache
            cached_result = get_from_cache(cache_key, cache_backend)
            if cached_result is not None:
                return cached_result

            # Executar função
            result = func(*args, **kwargs)

            # Armazenar no cache
            set_in_cache(cache_key, result, ttl, cache_backend)

            return result

        return wrapper
    return decorator
```

### Validation Decorators

#### @validate_json

```python
def validate_json(schema):
    """Decorador para validação de JSON de entrada.

    Args:
        schema (dict): Schema de validação

    Returns:
        function: Decorador de validação

    Example:
        user_schema = {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'email': {'type': 'string', 'format': 'email'}
            },
            'required': ['name', 'email']
        }

        @validate_json(user_schema)
        def create_user():
            data = request.get_json()  # Já validado
            return create_user_logic(data)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not request.is_json:
                raise ValidationError("Content-Type deve ser application/json")

            data = request.get_json()

            # Validar contra schema
            try:
                validate(data, schema)
            except ValidationError as e:
                raise ValidationError(f"Dados inválidos: {e.message}")

            return func(*args, **kwargs)

        return wrapper
    return decorator
```

### Rate Limiting Decorators

#### @rate_limit

```python
def rate_limit(requests_per_minute=60, per_user=True):
    """Decorador para rate limiting.

    Args:
        requests_per_minute (int): Limite de requisições por minuto
        per_user (bool): Se True, limite por usuário

    Returns:
        function: Decorador de rate limiting

    Example:
        @rate_limit(requests_per_minute=30)
        def api_endpoint():
            return {"data": "response"}
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Identificar cliente
            if per_user and has_request_context():
                client_id = get_jwt_identity() or request.remote_addr
            else:
                client_id = request.remote_addr

            # Verificar rate limit
            if is_rate_limited(client_id, requests_per_minute):
                raise RateLimitError("Muitas requisições. Tente novamente mais tarde.")

            # Incrementar contador
            increment_request_count(client_id)

            return func(*args, **kwargs)

        return wrapper
    return decorator
```

### Error Handling Decorators

#### @handle_errors

```python
def handle_errors(error_map=None, default_status=500):
    """Decorador para tratamento automático de erros.

    Args:
        error_map (dict): Mapeamento de exceções para status HTTP
        default_status (int): Status padrão para erros não mapeados

    Returns:
        function: Decorador de tratamento de erros

    Example:
        error_map = {
            ValidationError: 400,
            NotFoundError: 404,
            PermissionError: 403
        }

        @handle_errors(error_map)
        def api_endpoint():
            # Código que pode gerar exceções
            pass
    """
    if error_map is None:
        error_map = {}

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Verificar mapeamento de erro
                status_code = error_map.get(type(e), default_status)

                # Log do erro
                logger = get_logger(func.__module__)
                logger.error(f"Erro em {func.__name__}: {e}", exc_info=True)

                # Retornar resposta de erro
                return jsonify({
                    'error': type(e).__name__,
                    'message': str(e),
                    'timestamp': datetime.now().isoformat()
                }), status_code

        return wrapper
    return decorator
```

## Uso Combinado

### Endpoint Completo

```python
@app.route('/api/bots/<int:bot_id>/execute', methods=['POST'])
@CrossDomain(origin='*', methods=['POST'])
@jwt_required_custom()
@require_permissions('bot_execute')
@validate_json(bot_execution_schema)
@rate_limit(requests_per_minute=10)
@log_execution(level='INFO', include_args=True)
@audit_log('EXECUTE', 'BOT')
@handle_errors(api_error_map)
def execute_bot(bot_id):
    """Endpoint completo com todos os decoradores."""
    data = request.get_json()
    user_id = get_jwt_identity()

    result = bot_controller.execute_bot(bot_id, user_id, data)
    return jsonify(result)
```

## Configuração

### Settings

```python
DECORATOR_SETTINGS = {
    'jwt': {
        'algorithm': 'HS256',
        'expires_delta': timedelta(hours=1)
    },
    'rate_limit': {
        'redis_url': 'redis://localhost:6379/1',
        'default_limit': 100
    },
    'cache': {
        'default_ttl': 300,
        'redis_url': 'redis://localhost:6379/2'
    }
}
```
