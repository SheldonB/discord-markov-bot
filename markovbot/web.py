import logging

from aiohttp import web

from markovbot import markovbot

log = logging.getLogger(__name__)

async def health(request):
    log.debug('Received Health Check Request')

    health_resp = {
        'isReady': markovbot.is_ready(),
        'connectedGuildCount': markovbot.connect_guild_count
    }

    return web.json_response(health_resp)

app = web.Application()
app.add_routes([web.get('/health', health)])