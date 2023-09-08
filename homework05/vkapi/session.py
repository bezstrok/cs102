import typing as tp
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class Session:
    """
    Сессия.

    :param base_url: Базовый адрес, на который будут выполняться запросы.
    :param timeout: Максимальное время ожидания ответа от сервера.
    :param max_retries: Максимальное число повторных запросов.
    :param backoff_factor: Коэффициент экспоненциального нарастания задержки.
    """

    def __init__(
        self,
        base_url: str,
        timeout: float = 5.0,
        max_retries: int = 3,
        backoff_factor: float = 0.3,
        default_query_params: tp.Optional[tp.Dict[str, tp.Union[str, int]]] = None,
    ) -> None:
        self.base_url: str = base_url
        self.timeout: float = timeout

        self.session = requests.Session()
        self.session.params = default_query_params  # type: ignore
        self.session.mount(
            self.base_url,
            HTTPAdapter(
                max_retries=Retry(
                    total=max_retries,
                    backoff_factor=backoff_factor,
                    status_forcelist=frozenset(i for i in range(400, 527)),
                )
            ),
        )

    def _request(self, method: str, url: str, *args: tp.Any, **kwargs: tp.Any) -> requests.Response:
        kwargs.setdefault("timeout", self.timeout)
        full_url = urljoin(self.base_url, url)
        return self.session.request(method, full_url, *args, **kwargs)

    def get(self, url: str, *args: tp.Any, **kwargs: tp.Any) -> requests.Response:
        return self._request("GET", url, *args, **kwargs)

    def post(self, url: str, *args: tp.Any, **kwargs: tp.Any) -> requests.Response:
        return self._request("POST", url, *args, **kwargs)
