import asyncio
from asyncio import Future
import logging
import platform
from typing import Optional, Tuple
from urllib.parse import urljoin

import aiohttp
from aiohttp.client import ClientResponse
from aiortc import RTCConfiguration, RTCIceServer, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


WHIP_SERVER_URL: str = 'http://localhost:8080/whip'
ICE_SERVER_LIST = [RTCIceServer('stun:stun.l.google.com:19302'),]
# ICE_SERVER_LIST = [RTCIceServer('stun:stun.l.google.com:19302'),RTCIceServer('stun:stun.cloudflare.com:19302'),]


async def call_api(method: str, base_url: str, path: Optional[str] = '', headers: Optional[dict] = None, data: Optional[dict] = None) -> Optional[ClientResponse]:
    if path and not base_url.endswith('/'):
        url: str = urljoin(base_url + '/', path)
    elif path:
        url: str = urljoin(base_url, path)
    else:
        url: str = base_url

    response: Optional[ClientResponse] = None
    timeout = aiohttp.ClientTimeout()

    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.request(method, url, data=data, headers=headers) as resp:
                if not resp.ok:
                    logging.error(f'response.status: {resp.status}')
                else:
                    await resp.read()
                    response = resp
        except aiohttp.ClientError as e:
            logging.error(e)
            return None

    return response


def get_tracks() -> Tuple[MediaPlayer, Optional[MediaPlayer]]:
    video_options: dict = {'framerate': '30', 'video_size': '640x480'}
    match platform.system():
        case 'Darwin':
            webcam: MediaPlayer = MediaPlayer('default:default', format='avfoundation', options=video_options)
            audio = None
        case 'Linux':
            webcam: MediaPlayer = MediaPlayer('/dev/video0', format='v4l2', options=video_options)
            audio: MediaPlayer = MediaPlayer('default', format='pulse')
        case 'Windows':
            webcam: MediaPlayer = MediaPlayer('video=Integrated Camera', format='dshow', options=video_options)
            audio = None
    return webcam, audio


async def send_offer(local_sdp: str, url: str) -> Optional[str]:
    headers: dict = {'Content-Type': 'application/sdp'}

    response = await call_api('post', WHIP_SERVER_URL, data=local_sdp, headers=headers)
    if response.status not in (200, 201):
        logging.error('response.status')
        return

    return await response.text()


async def apply_answer(pc: RTCPeerConnection, remote_sdp: str) -> None:
    await pc.setRemoteDescription(RTCSessionDescription(sdp=remote_sdp, type='answer'))
    return


async def create_peer_connection() -> Optional[RTCPeerConnection]:
    pc: RTCPeerConnection = RTCPeerConnection(RTCConfiguration(ICE_SERVER_LIST))

    webcam: MediaPlayer
    audio: Optional[MediaPlayer]
    webcam, audio = get_tracks()

    pc.addTransceiver(webcam.video, direction='sendonly')

    if audio is not None:
        logging.info('use audio')
        pc.addTrack(audio.audio)
    else:
        try:
            pc.addTrack(webcam.audio)
            logging.info('use webcam audio')
        except Exception as e:
            logging.error(e)
            pass

    offer: RTCSessionDescription = await pc.createOffer()
    await pc.setLocalDescription(offer)
    logging.debug(f'local sdp: {pc.localDescription.sdp}')

    remote_sdp: Optional[str] = await send_offer(pc.localDescription.sdp, WHIP_SERVER_URL)
    if not remote_sdp:
        return

    logging.debug(f'remote sdp: {remote_sdp}')
    await apply_answer(pc, remote_sdp)

    return pc


# pionのwhip-whep exampleはDELETEに対応していないので使わない
async def on_shutdown(pc: RTCPeerConnection) -> None:
    logging.info('on_shutdown')

    try:
        response = await call_api('post', WHIP_SERVER_URL)
        logging.info(response)
    except Exception as e:
        logging.error(e)

    if pc:
        await pc.close()


async def create_whip_connection() -> Optional[RTCPeerConnection]:
    pc = await create_peer_connection()
    return pc


# todo:  update not to use asyncio low level loop API
def run():
    pc: Optional[RTCPeerConnection] = None

    loop = asyncio.new_event_loop()
    create_whip_connection_task: Future = create_whip_connection()

    try:
        pc: Optional[RTCPeerConnection] = loop.run_until_complete(create_whip_connection_task)
        loop.run_forever()
    except KeyboardInterrupt:
        logging.error('KeyboardInterrupt')
    except Exception as e:
        logging.error(e)
    finally:
        on_shutdown_task: Future = on_shutdown(pc)
        loop.run_until_complete(on_shutdown_task)
        loop.stop()


if __name__ == '__main__':
    run()
