import asyncio
import time

from loguru import logger

from gpiozero import LED, Button
from gpiozero.pins.pigpio import PiGPIOFactory


class GPIOManager:
    # ピン設定
    __PIN_RELAY_SWITCH = 21
    __PIN_RELAY_SWITCH2 = 20
    __PIN_LED1 = 16  # 12
    __PIN_BTN1 = 6

    __MINIMUM_SLEEP_SECONDS = 0.1
    __DEBUG_DUMMY_SECONDS = 0.1

    def __init__(self, debug: bool = False):
        logger.info("Factory initializing...")
        self.debug = debug
        if self.debug:
            self._factory = None
            self._relay_pin = None
            self._relay_pin2 = None
            self._led_pin = None
            self._btn_pin = None
        else:
            self._factory = PiGPIOFactory()
            self._relay_pin = LED(self.__PIN_RELAY_SWITCH, pin_factory=self._factory)
            self._relay_pin2 = LED(self.__PIN_RELAY_SWITCH2, pin_factory=self._factory)
            self._led_pin = LED(self.__PIN_LED1, pin_factory=self._factory)
            self._btn_pin = Button(self.__PIN_BTN1, pull_up=True, pin_factory=self._factory)

    def _get_relay_pin(self, sub: bool = False) -> LED:
        return self._relay_pin2 if sub else self._relay_pin

    async def relay_on(self, sub: bool = False):
        if self.debug:
            await asyncio.sleep(self.__DEBUG_DUMMY_SECONDS)
            logger.info("MOCK RELAY ON- AC:ON")
        else:
            # ACの制御
            self._get_relay_pin(sub).on()
            logger.debug("relay on - AC:ON")
        # async sleep 中は他task実行許可あり
        await asyncio.sleep(self.__MINIMUM_SLEEP_SECONDS)

    def relay_on_sync(self, sub: bool = False):
        if self.debug:
            time.sleep(self.__DEBUG_DUMMY_SECONDS)
            logger.info("MOCK RELAY ON- AC:ON")
        else:
            self._get_relay_pin(sub).on()
            logger.debug("relay on - AC:ON")
        # 安全マージン
        time.sleep(self.__MINIMUM_SLEEP_SECONDS)

    async def relay_off(self, sub: bool = False):
        if self.debug:
            time.sleep(self.__DEBUG_DUMMY_SECONDS)
            logger.info("MOCK RELAY OFF- AC:OFF")
        else:
            self._get_relay_pin(sub).off()
            logger.debug("relay off - AC:OFF")
        # 安全マージン
        await asyncio.sleep(self.__MINIMUM_SLEEP_SECONDS)

    def relay_off_sync(self, sub: bool = False):
        if self.debug:
            time.sleep(self.__DEBUG_DUMMY_SECONDS)
            logger.info("MOCK RELAY OFF- AC:OFF")
        else:
            self._get_relay_pin(sub).off()
            logger.debug("relay off - AC:OFF")
        # 安全マージン
        time.sleep(self.__MINIMUM_SLEEP_SECONDS)

    async def led_on(self):
        # 明るさ制御なら別
        # https://zenn.dev/kotaproj/books/raspberrypi-tips/viewer/011_kiso_ledpwm
        if self.debug:
            await asyncio.sleep(self.__DEBUG_DUMMY_SECONDS)
            logger.debug("MOCK LED ON")
            return
        else:
            logger.debug("LED ON")
            self._led_pin.on()

    async def led_off(self):
        if self.debug:
            await asyncio.sleep(self.__DEBUG_DUMMY_SECONDS)
            logger.debug("MOCK LED OFF")
            return
        else:
            logger.debug("LED OFF")
            self._led_pin.off()

    async def led_blink(self, seconds: float):
        if self.debug:
            await asyncio.sleep(self.__DEBUG_DUMMY_SECONDS)
            logger.debug(f"MOCK LED BLINK - SECONDS: {seconds}")
            return
        else:
            logger.debug(f"LED BLINK - SECONDS: {seconds}")
            self._led_pin.blink()
            await asyncio.sleep(seconds)
            self._led_pin.off()

    def led_blink_sync(self, seconds: float):
        if self.debug:
            time.sleep(self.__DEBUG_DUMMY_SECONDS)
            logger.debug(f"MOCK LED BLINK - SECONDS: {seconds}")
            return
        else:
            logger.debug(f"LED BLINK - SECONDS: {seconds}")
            self._led_pin.blink()
            time.sleep(seconds)
            self._led_pin.off()

    async def led_toggle(self):
        if self.debug:
            await asyncio.sleep(self.__DEBUG_DUMMY_SECONDS)
            logger.debug("MOCK LED TOGGLE")
            return
        else:
            logger.debug("LED TOGGLE")
            self._led_pin.toggle()

    async def is_button_pressed(self) -> bool:
        """ Check button pressed(with sleep __MINIMUM_SLEEP_SECONDS)
        :return:
        """
        await asyncio.sleep(self.__MINIMUM_SLEEP_SECONDS)
        if self._btn_pin is not None and isinstance(self._btn_pin, Button):
            # https://www.jetbrains.com/help/pycharm/disabling-and-enabling-inspections.html
            # noinspection PyUnresolvedReferences
            return self._btn_pin.is_pressed  # pylint: disable=E1101
        return False

# Lチカ
# for _ in range(5):
#     await manager.led_on()
#     await asyncio.sleep(0.5)
#     await manager.led_off()
#     await asyncio.sleep(0.5)
#
# await manager.led_blink(6.0)
# for i in range(20):
#     await manager.led_toggle()
#     await asyncio.sleep(0.1)
