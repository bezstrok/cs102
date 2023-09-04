import textwrap
import time
import typing as tp
from string import Template

import pandas as pd
from pandas import json_normalize

from vkapi import config, session
from vkapi.exceptions import APIError
from vkapi.friends import assert_response_ok

from .constants import POST_CODE_REQUESTS_LIMIT, REQUEST_DELAY, WALL_GET_COUNT_LIMIT


def get_posts_2500(
    owner_id: str = "",
    domain: str = "",
    offset: int = 0,
    count: int = 10,
    filter: str = "owner",
    extended: int = 0,
    fields: tp.Optional[tp.List[str]] = None,
    *,
    timeout: float = 15.0,
) -> tp.Dict[str, tp.Any]:
    count_limited: int = min(count, POST_CODE_REQUESTS_LIMIT * WALL_GET_COUNT_LIMIT)

    code: str = f"""
        var count = {count_limited};
        var offset = {offset};
        var response = [];

        while(count > 0) {{
            response.push(
                API.wall.get({{
                    "owner_id": "{owner_id}",
                    "domain": "{domain}",
                    "offset": offset,
                    "count": count,
                    "filter": "{filter}",
                    "extended": "{extended}",
                    "fields": "{fields}"
                }})
            );

            offset = offset + {WALL_GET_COUNT_LIMIT};
            count = count - {WALL_GET_COUNT_LIMIT};
        }}

        return response;"""

    responses = session.post("execute", data={"code": code}, timeout=timeout)

    assert_response_ok(responses)

    responses_data = responses.json()["response"]
    combined_responses_data: tp.Dict[str, tp.Dict[str, tp.Any]] = {"response": {}}

    for response in responses_data:
        for key, value in response.items():
            if isinstance(value, list):
                combined_responses_data["response"].setdefault(key, []).extend(value)
            else:
                combined_responses_data["response"].setdefault(key, value)

    return combined_responses_data


def get_wall_execute(
    owner_id: str = "",
    domain: str = "",
    offset: int = 0,
    count: int = 10,
    max_count: int = 2500,
    filter: str = "owner",
    extended: int = 0,
    fields: tp.Optional[tp.List[str]] = None,
    progress=None,
) -> pd.DataFrame:
    """
    Возвращает список записей со стены пользователя или сообщества.

    @see: https://vk.com/dev/wall.get

    :param owner_id: Идентификатор пользователя или сообщества, со стены которого необходимо получить записи.
    :param domain: Короткий адрес пользователя или сообщества.
    :param offset: Смещение, необходимое для выборки определенного подмножества записей.
    :param count: Количество записей, которое необходимо получить (0 - все записи).
    :param max_count: Максимальное число записей, которое может быть получено за один запрос.
    :param filter: Определяет, какие типы записей на стене необходимо получить.
    :param extended: 1 — в ответе будут возвращены дополнительные поля profiles и groups, содержащие информацию о пользователях и сообществах.
    :param fields: Список дополнительных полей для профилей и сообществ, которые необходимо вернуть.
    :param progress: Callback для отображения прогресса.
    """
    pass
