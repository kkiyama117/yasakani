from loguru import logger
from fastapi import Request, FastAPI, HTTPException, APIRouter
from linebot.v3.webhook import WebhookParser
from linebot.v3.messaging import (
    AsyncApiClient,
    AsyncMessagingApi,
    Configuration,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent, UserSource, GroupSource, RoomSource
)

from kizaru.utils.notify import LineManager
from kizaru.secret import Secrets


class LineServer:
    def __init__(self):
        self.line_manager = LineManager()
        self.secrets = Secrets()
        self.router = APIRouter()
        self.router.add_api_route("/callback", self.line_callback, methods=["POST"])

    async def line_callback(self, request: Request):
        parser = self.line_manager.line_webhook_parser
        signature = request.headers.get('X-Line-Signature')

        # get request body as text
        body = await request.body()
        body = body.decode()

        # parse events
        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError as e:
            logger.error(e)
            raise HTTPException(status_code=400, detail="Invalid signature")

        for event in events:
            # check if this is text message
            if not isinstance(event, MessageEvent):
                continue
            if not isinstance(event.message, TextMessageContent):
                continue

            await self.line_manager.reply_msg(
                _reply_generator=self.__rg, event=event)

        return 'OK'

    def __rg(self, event):
        return reply_generator(event, self.secrets)


async def reply_generator(event, secrets: Secrets) -> [str, list[TextMessage]]:
    result_messages = []
    if isinstance(event, MessageEvent) and isinstance(event.message, TextMessageContent):
        _text = event.message.text
        if _text.startswith('probability'):
            try:
                _text_list = _text.split()
                _prob = float(_text_list[1])
                await secrets.set_lottery_float(_prob)
                result_messages.append(TextMessage(text=f"{_prob}の割合で当てるよぉ~~~"))
            except Exception as e:
                result_messages.append(TextMessage(text="良く分からないねぇ~"))
                result_messages.append(TextMessage(text=f"エラーだねぇ:{e}"))
        elif _text.startswith('add'):
            try:
                _source = event.source
                if isinstance(_source, UserSource):
                    _id = _source.user_id
                elif isinstance(_source, GroupSource):
                    _id = _source.group_id
                elif isinstance(_source, RoomSource):
                    _id = _source.room_id
                else:
                    _id = ""
                    raise ValueError("Invalid source type")
                await secrets.add_id_list(_id)
                result_messages.append(TextMessage(text=f"{_source}に伝えなきゃねぇ~~~"))
            except Exception as e:
                result_messages.append(TextMessage(text="良く分からないねぇ~"))
                result_messages.append(TextMessage(text=f"エラーだねぇ:{e}"))
        else:
            result_messages.append(TextMessage(text="良く分からないねぇ~"))
    else:
        result_messages.append(TextMessage(text="良く分からないねぇ~"))

        # return event.reply_token, [TextMessage(text=event.message.text)]
    return event.reply_token, result_messages


app = FastAPI()
line_server = LineServer()
app.include_router(line_server.router)
