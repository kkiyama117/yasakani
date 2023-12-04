import random
from datetime import datetime

from loguru import logger

from kizaru.secret import Secrets


async def shirohige_death_lottery(debug: bool = False, force=False) -> bool:
    """

    :param debug: debug mode
    :param force: Force Shirohige death
    :return: whether Shirohige is dead or not
    """
    logger.debug(f"SHIROHIGE CHECK")
    base = await Secrets().get_lottery_float()
    random.seed(datetime.now().timestamp())
    # 乱数生成
    if force:
        r = 0
    else:
        r = random.random()
    logger.debug(f"SHIROHIGE CHECK - {r}")
    if r <= base:
        logger.info(f"SHIROHIGE DEATH!!!")
        return True
    return False
