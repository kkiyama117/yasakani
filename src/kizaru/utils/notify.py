import asyncio
import uuid

from linebot.v3 import WebhookParser
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    MessagingApi, TextMessage, Configuration, PushMessageRequest, AsyncApiClient, AsyncMessagingApi,
    PushMessageResponse, ReplyMessageRequest, ReplyMessageResponse,
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)
from loguru import logger
import notifiers
from xdg_base_dirs import xdg_data_home

from kizaru.secret import Secrets


class LineManager:
    __instance = None
    __data_file = None
    # secrets
    LINE_FALLBACK_TOKEN = None
    __self_user_id = None
    __line_bot_config = None
    line_webhook_parser = None

    def __new__(cls, *args, **kargs):
        if not hasattr(cls, "__instance"):
            cls.__instance = super(LineManager, cls).__new__(cls)
            logger.info("Line Bot initializing...")
            secrets = Secrets()
            cls.LINE_FALLBACK_TOKEN = secrets.LINE_FALLBACK_TOKEN
            cls.__self_user_id = secrets.LINE_SELF_USER_ID
            cls.__line_bot_config = Configuration(access_token=secrets.LINE_CHANNEL_ACCESS_TOKEN)
            cls.line_webhook_parser = WebhookParser(secrets.LINE_CHANNEL_SECRET)
            # check if data_dir exists
            _dh = xdg_data_home() / "kizaru"
            _dh.mkdir(parents=True, exist_ok=True)
            cls.__data_file = _dh / "secrets.json"
            cls.__data_file.touch(mode=0o644)

            cls.__instance.__initialized = False
        return cls.__instance

    async def reply_msg(self, _reply_generator, event, fail_safe=False) -> ReplyMessageResponse | None:
        """Reply message wrapper

        :param _reply_generator: return(ReplyMessageResponse,reply_token)
        :param event:
        :param fail_safe:
        :return:
        """
        if fail_safe:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self.__send_msg_fail_safe, "fail_safe_mode")
        async with AsyncApiClient(LineManager.__line_bot_config) as api_client:
            api_instance = AsyncMessagingApi(api_client)
            reply_token, messages = await _reply_generator(event)
            message_request = ReplyMessageRequest(reply_token=reply_token, messages=messages)
            return await api_instance.reply_message(message_request)

    async def send_msg(self, msg: str, only_me=False, fail_safe=False) \
            -> PushMessageResponse | tuple[PushMessageResponse] | None:
        logger.debug("send_msg_by_line")
        # fail_safe_mode
        if fail_safe:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self.__send_msg_fail_safe, msg)
        # messaging mode
        async with AsyncApiClient(LineManager.__line_bot_config) as api_client:
            api_instance = AsyncMessagingApi(api_client)
            message = TextMessage(text=msg)
            if only_me:
                push_msg = PushMessageRequest(to=LineManager.__self_user_id, messages=[message])
                x_line_retry_key = uuid.uuid4()
                try:
                    api_res = await api_instance.push_message(push_msg, x_line_retry_key=str(x_line_retry_key))
                    return api_res
                except Exception as e:
                    logger.error(e)
            else:
                secrets = Secrets()
                id_list = (await secrets.get_current_data()).get("id_list", [])
                job_list = []
                for _id in id_list:
                    push_msg = PushMessageRequest(to=_id, messages=[message])
                    x_line_retry_key = uuid.uuid4()
                    _job = api_instance.push_message(push_msg, x_line_retry_key=str(x_line_retry_key))
                    job_list.append(_job)
                try:
                    results = await asyncio.gather(*job_list)
                except Exception as e:
                    logger.error(e)
                return results

    @staticmethod
    def __send_msg_fail_safe(msg):
        import requests
        url = "https://notify-api.line.me/api/notify"
        headers = {"Authorization": "Bearer " + LineManager.LINE_FALLBACK_TOKEN}
        params = {"message": msg}
        r = requests.post(url, headers=headers, params=params)
        logger.debug(r.text)


async def send_email(debug: bool = True, send_to_others=False, **kwargs):
    secrets = Secrets()
    notifier = notifiers.get_notifier("gmail", strict=True)
    params = secrets.MAIL_NOTIFIERS_PARAM.copy()
    # DEFAULT MESSAGE
    params.update({"subject": "KIZARU App is start", "message": "KIZARU is running!"})
    if send_to_others:
        params.update(to=secrets.MAIL_TO_ALL)
    params.update(kwargs)
    if debug:
        logger.debug(f"mail is not send (DEBUG mode)")
        logger.debug(params)
    else:
        logger.debug(params)
        # get asyncio loop
        loop = asyncio.get_event_loop()

        def _notify(kargs):
            return notifier.notify(**kargs)

        mail = await loop.run_in_executor(
            None, _notify, params
        )
        logger.debug(f"MAIL sent: {mail}")
