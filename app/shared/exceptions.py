class DominioError(Exception):
    """Error controlado de negocio."""

    def __init__(self, codigo: str, mensaje: str, status_code: int = 400):
        super().__init__(mensaje)
        self.codigo = codigo
        self.mensaje = mensaje
        self.status_code = status_code
