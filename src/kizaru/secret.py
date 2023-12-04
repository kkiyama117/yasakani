import os
import json
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger
from xdg_base_dirs import xdg_data_home

load_dotenv(dotenv_path=str(Path.cwd() / ".env"))
LOTTERY_FLOAT_KEY = "lottery_float"
LINE_ID_LIST_KEY = "line_id_list"


class Secrets:
    __instance = None
    __data_file = None

    def __new__(cls, *args, **kargs):
        if not hasattr(cls, "__instance"):
            cls.__instance = super(Secrets, cls).__new__(cls)
            logger.info("Secret initializing...")
            cls.MAIL_NOTIFIERS_PARAM = {
                "username": os.getenv("MAIL_USERNAME"),
                "password": os.getenv("MAIL_PASSWORD"),
                "to": json.loads(os.getenv("MAIL_TO"))
            }
            cls.MAIL_TO_ALL = json.loads(os.getenv("MAIL_TO_ALL"))
            cls.PROGRAM_PATH = os.getenv("PROGRAM_PATH")
            cls.PROGRAM_LOCAL_PATH = os.getenv("PROGRAM_LOCAl_PATH")
            cls.LINE_FALLBACK_TOKEN = os.getenv("LINE_FALLBACK_TOKEN")
            cls.LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
            cls.LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
            cls.LINE_SELF_USER_ID = os.getenv("LINE_SELF_USER_ID")
            # check if data_dir exists
            _dh = xdg_data_home() / "kizaru"
            _dh.mkdir(parents=True, exist_ok=True)
            __data_file = _dh / "secrets.json"
            if not __data_file.exists():
                cls.__data_file.touch(mode=0o644)
                cls.__data_file.write_text(json.dumps({LOTTERY_FLOAT_KEY: 0.03}))
            cls.__data_file = __data_file

            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self, debug: bool = False):
        self.__data_file = Secrets.__data_file

    async def get_current_data(self) -> dict:
        with self.__data_file.open("r") as file:
            return json.loads(file.read())

    async def set_data(self, data: dict):
        with self.__data_file.open("r+") as file:
            base = json.load(file)
            new_data = base | data
            file.seek(0)
            file.truncate()
            json.dump(new_data, file, indent=4)

    async def get_lottery_float(self) -> float:
        """ Default is 0.03

        :return:
        """
        _data = await self.get_current_data()
        return _data.get(LOTTERY_FLOAT_KEY, 0.03)

    async def set_lottery_float(self, value: float):
        """ Default is 0.03

        :return:
        """
        await self.set_data({LOTTERY_FLOAT_KEY: value})

    async def get_id_list(self) -> list[str]:
        _data = await self.get_current_data()
        return _data.get(LINE_ID_LIST_KEY, [])

    async def set_id_list(self, value: list):
        await self.set_data({LINE_ID_LIST_KEY: value})

    async def add_id_list(self, value: str):
        _data: list[str] = await self.get_id_list()
        _data.append(value)
        await self.set_data({LINE_ID_LIST_KEY: list(set(_data))})
