from vkapi import config
from vkapi.session import Session

session = Session(
    config.VK_CONFIG["domain"],
    default_query_params={
        "access_token": config.VK_CONFIG["access_token"],
        "v": config.VK_CONFIG["version"],
    },
)
