import sys

import asyncio
from loguru import logger

from kizaru.one_sequence import call_once
from kizaru.gpio import GPIOManager
from kizaru.utils import setup_logger, send_email
from kizaru.utils.notify import LineManager


async def main_loop(debug: bool = False) -> None:
    # Initialize ==============================
    # initialize(logger)
    setup_logger(debug)
    line_bot = LineManager()
    logger.info("calling main_loop...")
    # ==============================
    if debug:
        sound_debug = False
        relay_debug = True
    else:
        sound_debug = False
        relay_debug = False
    # ピン設定(falseでダミー)
    manager = GPIOManager(relay_debug)
    # ==============================
    # LEDで通電確認
    manager.led_blink_sync(2.0)
    await manager.relay_off()
    await manager.relay_off(sub=True)
    # MAIN LOOP
    try:
        if debug:
            pass
            while True:
                await asyncio.sleep(2.0)
                logger.debug("button pressed")
                await call_once(manager, sound_debug=sound_debug)
        else:
            while True:
                if await manager.is_button_pressed():
                    logger.debug("button pressed")
                    await call_once(manager, sound_debug=sound_debug)
                else:
                    pass
    except (KeyboardInterrupt, asyncio.CancelledError) as e:
        logger.info("main loop is cancelled (maybe due to KeyboardInterrupt)")
        await send_email(debug, send_to_others=False,
                         subject="STOP MAIN LOOP by Cancelled",
                         message=f"STOP LOG is like below\n{e}")
    except Exception as e:
        logger.error(logger.opt(exception=e).info("STOP_MAIN LOOP BY EXCEPTION!!"))
        await line_bot.send_msg("怖いねぇ~\n黄猿も死んだよぉ~", only_me=True)
        await send_email(debug, send_to_others=True,
                         subject="STOP MAIN LOOP BY UNKNOWN EXCEPTION!!!",
                         message=f"ERROR is like below\n{e}")
        raise e
    finally:
        manager.led_blink_sync(2.0)
        manager.relay_off_sync()
        logger.info("FINALIZER CALLED SUCCESSFULLY")
        sys.exit(0)


async def main(debug: bool = False):
    await main_loop(debug)


if __name__ == "__main__":
    # SWITCH if DEBUG or not
    args = sys.argv
    if len(args) >= 2 and args[1] == "dev_local":
        _debug = True
    else:
        _debug = False
    asyncio.run(main(_debug))
