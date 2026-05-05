def respuesta_ok(mensaje: str, datos: dict | list | None = None) -> dict:
    return {'ok': True, 'mensaje': mensaje, 'datos': datos}
