import asyncio

from loguru import logger

from kizaru.sound import play_sound, init_sound
from kizaru.gpio import GPIOManager
from kizaru.utils import shirohige_death_lottery, send_email
from kizaru.utils.notify import LineManager


async def delayed_sub(manager: GPIOManager, sec: float = 2.0):
    await asyncio.sleep(sec)
    await manager.relay_on(sub=True)


async def call_once(manager: GPIOManager, sound_debug: bool = False) -> bool:
    logger.debug("start job")
    # 確認用LED
    await manager.led_on()
    # 抽選
    shirohige_death = await shirohige_death_lottery()
    _tasks = []
    # 音がでるやつ
    task_sound = init_sound(debug=sound_debug)
    _tasks.append(task_sound)
    # 光るやつ
    task_light = manager.relay_on()
    _tasks.append(task_light)
    if shirohige_death:
        task_light2 = delayed_sub(manager)
        _tasks.append(task_light2)
    # 通知
    if shirohige_death:
        task_notify1 = death_mail()
        task_notify2 = death_line()
        _tasks.append(task_notify1)
        _tasks.append(task_notify2)
    await asyncio.gather(*_tasks)
    # 消す
    _tasks2 = [manager.relay_off()]
    if shirohige_death:
        _tasks2.append(manager.relay_off(sub=True))
    await asyncio.gather(*_tasks2)
    # 音がでるやつ(with 当たり判定)
    await play_sound(shirohige_death, debug=sound_debug)
    await manager.led_off()
    return True


async def death_mail(debug: bool = False):
    if debug:
        _sub = "(DEBUG)"
    else:
        _sub = ""
    subject = f"{_sub}SHIROHIGE DEATH!!!"
    return await send_email(debug=debug, send_to_others=True, subject=subject, message=f"Killed by Kizaru")


async def death_line(debug: bool = False):
    line = LineManager()
    msg = f"移動もさせない…ムダだよォ～今死ぬよォ～～～!!!"
    if debug:
        logger.debug("DEATH LINE")
        logger.debug(f"{msg}")
    else:
        pass
    return await line.send_msg(msg)
