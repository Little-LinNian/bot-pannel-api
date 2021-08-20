import asyncio
import aiohttp
import uvicorn
from avilla.event.message import MessageEvent
import api
from avilla import Avilla
from avilla.network.clients.aiohttp import AiohttpWebsocketClient
from avilla.onebot.config import OnebotConfig, WebsocketCommunication
from avilla.onebot.protocol import OnebotProtocol
from graia.broadcast import Broadcast
from graia.saya import Saya
from graia.saya.builtins.broadcast import BroadcastBehaviour
from loguru import logger
from yarl import URL


logger.add("./cache/debuglogs", level="DEBUG")
loop = asyncio.get_event_loop()
bcc = Broadcast(loop=loop)
saya = Saya(broadcast=bcc)
saya.install_behaviours(BroadcastBehaviour(bcc))
session = aiohttp.ClientSession(loop=loop)
app = Avilla(
    bcc,
    OnebotProtocol,
    {"ws": AiohttpWebsocketClient(session)},
    {
        OnebotProtocol: OnebotConfig(
            access_token="",
            bot_id=2747804982,
            communications={
                "ws": WebsocketCommunication(api_root=URL("ws://localhost:6700/"))
            },
        )
    },
    logger=logger
)


api_launched = False


@bcc.receiver(MessageEvent)
async def on_launch():
    global api_launched
    if api_launched:
        return
    api_launched = True
    app.logger.debug("Try to launch api")
    api.saya = saya

    api.avilla = app
    await asyncio.to_thread(uvicorn.run, app=api.app, host="0.0.0.0", port=7050)
try:
    app.launch_blocking()
except KeyboardInterrupt:
    quit()
