import dataclasses
import math
import time
import typing as tp

import requests

from vkapi import config, session
from vkapi.exceptions import APIError

QueryParams = tp.Optional[tp.Dict[str, tp.Union[str, int]]]


def assert_response_ok(response: requests.Response) -> None:
    if response.status_code != 200:
        raise APIError(
            f"Unexpected status code: {response.status_code}. Response content: {response.text}"
        )

    try:
        response_data = response.json()
    except ValueError:
        raise APIError("Invalid JSON received from API.")

    if "error" in response_data:
        raise APIError(f"API Error: {response_data['error'].get('error_msg', 'Unknown error')}")


@dataclasses.dataclass(frozen=True)
class FriendsResponse:
    count: int
    items: tp.Union[tp.List[int], tp.List[tp.Dict[str, tp.Any]]]


def get_friends(
    user_id: int, count: int = 5000, offset: int = 0, fields: tp.Optional[tp.List[str]] = None
) -> FriendsResponse:
    """
    Получить список идентификаторов друзей пользователя или расширенную информацию
    о друзьях пользователя (при использовании параметра fields).

    :param user_id: Идентификатор пользователя, список друзей для которого нужно получить.
    :param count: Количество друзей, которое нужно вернуть.
    :param offset: Смещение, необходимое для выборки определенного подмножества друзей.
    :param fields: Список полей, которые нужно получить для каждого пользователя.
    :return: Список идентификаторов друзей пользователя или список пользователей.
    """
    response = session.get(
        "friends.get",
        params={
            "user_id": user_id,
            "count": count,
            "offset": offset,
            "fields": ",".join(fields) if fields else None,
        },
    )

    assert_response_ok(response)

    response_data = response.json()

    return FriendsResponse(response_data["response"]["count"], response_data["response"]["items"])


class MutualFriends(tp.TypedDict):
    id: int
    common_friends: tp.List[int]
    common_count: int


def get_mutual(
    source_uid: tp.Optional[int] = None,
    target_uid: tp.Optional[int] = None,
    target_uids: tp.Optional[tp.List[int]] = None,
    order: str = "",
    count: tp.Optional[int] = None,
    offset: int = 0,
    progress=None,
) -> tp.Union[tp.List[int], tp.List[MutualFriends]]:
    """
    Получить список идентификаторов общих друзей между парой пользователей.

    :param source_uid: Идентификатор пользователя, чьи друзья пересекаются с друзьями пользователя с идентификатором target_uid.
    :param target_uid: Идентификатор пользователя, с которым необходимо искать общих друзей.
    :param target_uids: Cписок идентификаторов пользователей, с которыми необходимо искать общих друзей.
    :param order: Порядок, в котором нужно вернуть список общих друзей.
    :param count: Количество общих друзей, которое нужно вернуть.
    :param offset: Смещение, необходимое для выборки определенного подмножества общих друзей.
    :param progress: Callback для отображения прогресса.
    """
    progress = progress or (lambda arg: arg)
    chunk_size: int = 100  # Users per a request
    request_delay: float = 1 / 3  # VKApi delay

    params = {"source_uid": source_uid, "order": order, "count": count, "offset": offset}

    if target_uid:
        params["target_uid"] = target_uid
        response = session.get("friends.getMutual", params=params)
        assert_response_ok(response)
        return response.json()["response"]

    if target_uids:
        result: tp.List[MutualFriends] = []

        for i in progress(range(0, len(target_uids), chunk_size)):
            params["target_uids"] = ",".join(map(str, target_uids[i : i + chunk_size]))
            params["offset"] = i
            response = session.get("friends.getMutual", params=params)

            assert_response_ok(response)

            for person in response.json()["response"]:
                result.append(
                    MutualFriends(
                        id=person["id"],
                        common_friends=person["common_friends"],
                        common_count=person["common_count"],
                    )
                )

            time.sleep(request_delay)

        return result

    raise APIError("Either target_uid or target_uids should be provided.")
