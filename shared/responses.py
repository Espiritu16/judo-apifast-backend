def respuesta_ok(message: str, data: dict | list | None = None) -> dict:
    return {'ok': True, 'message': message, 'data': data}
def respuesta_error(code: str, message: str, details: dict | None = None) -> dict:
    return {
        'ok': False,
        'error': {
            'code': code,
            'message': message,
            'details': details or {},
        },
    }