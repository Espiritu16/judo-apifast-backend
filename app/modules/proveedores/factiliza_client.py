import httpx

from app.core.config import settings
from app.shared.exceptions import DominioError


class FactilizaClient:
    def __init__(self) -> None:
        token = (settings.FACTILIZA_API_TOKEN or '').strip()
        if not token:
            raise DominioError(
                'EXTERNAL_SERVICE_UNAVAILABLE',
                'No se pudo consultar el servicio externo en este momento. Inténtalo nuevamente.',
                503,
            )

        self.base_url = settings.FACTILIZA_API_BASE_URL.rstrip('/')
        self.headers = {'Authorization': f'Bearer {token}'}
        self.timeout = settings.FACTILIZA_TIMEOUT_SECONDS

    def consultar_dni(self, dni: str) -> dict:
        return self._get(f'/dni/info/{dni}')

    def consultar_ruc(self, ruc: str) -> dict:
        return self._get(f'/ruc/info/{ruc}')

    def _get(self, path: str) -> dict:
        url = f'{self.base_url}{path}'
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=self.headers)
        except httpx.TimeoutException as exc:
            raise DominioError(
                'EXTERNAL_SERVICE_UNAVAILABLE',
                'No se pudo consultar el servicio externo en este momento. Inténtalo nuevamente.',
                503,
            ) from exc
        except httpx.HTTPError as exc:
            raise DominioError(
                'EXTERNAL_SERVICE_ERROR',
                'No se pudo consultar el servicio externo en este momento. Inténtalo nuevamente.',
                502,
            ) from exc

        if response.status_code in (404, 422):
            raise DominioError('RESOURCE_NOT_FOUND', 'No se encontraron datos para el documento ingresado.', 404)
        if response.status_code >= 500:
            raise DominioError(
                'EXTERNAL_SERVICE_UNAVAILABLE',
                'No se pudo consultar el servicio externo en este momento. Inténtalo nuevamente.',
                503,
            )
        if response.status_code >= 400:
            raise DominioError('VALIDATION_ERROR', 'No se encontraron datos para el documento ingresado.', 404)

        try:
            payload = response.json()
        except ValueError as exc:
            raise DominioError(
                'EXTERNAL_SERVICE_ERROR',
                'No se pudo consultar el servicio externo en este momento. Inténtalo nuevamente.',
                502,
            ) from exc

        if isinstance(payload, dict) and payload.get('success') is False:
            raise DominioError('RESOURCE_NOT_FOUND', 'No se encontraron datos para el documento ingresado.', 404)

        return payload
