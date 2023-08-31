import datetime as dt
import statistics
import typing as tp
from pprint import pprint
from time import perf_counter

from vkapi.exceptions import APIError
from vkapi.friends import get_friends


def age_predict(user_id: int) -> tp.Optional[float]:
    """
    Наивный прогноз возраста пользователя по возрасту его друзей.

    Возраст считается как медиана среди возраста всех друзей пользователя

    :param user_id: Идентификатор пользователя.
    :return: Медианный возраст пользователя.
    """
    try:
        people = get_friends(user_id, fields=["bdate"]).items
    except APIError:
        return None

    today = dt.date.today()

    ages = []
    for p in people:  # formats may be "dd.mm.yyyy" or "dd.mm" or doesn't exist
        if isinstance(p, dict) and "bdate" in p and p["bdate"].count(".") == 2:
            d, m, y = map(int, p["bdate"].split("."))
            age = today.year - y - ((today.month, today.day) < (m, d))
            ages.append(age)

    if not ages:
        return None

    return statistics.median(ages)
