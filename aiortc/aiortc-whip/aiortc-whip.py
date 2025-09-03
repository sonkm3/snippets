
import asyncio
import platform
from typing import Optional, Tuple
from urllib.parse import urljoin

import aiohttp
from aiohttp.client import ClientResponse
from aiortc import RTCConfiguration, RTCIceServer, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer


WHIP_SERVER_URL: str = 'http://localhost:8080/whip'
ICE_SERVER_LIST = [RTCIceServer('stun:stun.l.google.com:19302'),]
# ICE_SERVER_LIST = [RTCIceServer('stun:stun.l.google.com:19302'),RTCIceServer('stun:stun.cloudflare.com:19302'),]


async def call_api(method: str, base_url: str, path: Optional[str] = '', headers: Optional[dict] = None, data: Optional[dict] = None) -> Optional[ClientResponse]:
    if path and not base_url.endswith('/'):
        url:str = urljoin(base_url + '/', path)
    elif path:
        url:str = urljoin(base_url, path)
    else:
        url:str = base_url

    response: Optional[ClientResponse] = None
    async with aiohttp.ClientSession() as session:
        try:
            async with session.request(method, url, data=data, headers=headers) as resp:
                if not resp.ok:
                    print(f'response.status: {resp.status}')
                else:
                    await resp.read()
                    response = resp
        except aiohttp.ClientError as e:
            print(e)
            return None

    return response

def get_tracks() -> Tuple[MediaPlayer, Optional[MediaPlayer]]:
    video_options: dict = {'framerate': '30', 'video_size': '640x480'}
    match platform.system():
        case "Darwin":
            webcam: MediaPlayer = MediaPlayer('default:default', format='avfoundation', options=video_options)
            audio = None
        case "Linux":
            webcam: MediaPlayer = MediaPlayer('/dev/video0', format='v4l2', options=video_options)
            audio: MediaPlayer = MediaPlayer('default', format='pulse')
        case "Windows":
            webcam: MediaPlayer = MediaPlayer('video=Integrated Camera', format='dshow', options=video_options)
            audio = None
    return webcam, audio

async def send_offer(pc: RTCPeerConnection, url: str) -> Optional[str]:
    headers: dict = {'Content-Type': 'application/sdp'}
    local_sdp = pc.localDescription.sdp

    response = await call_api('post', WHIP_SERVER_URL, data=local_sdp, headers=headers)
    if response.status not in (200, 201):
        print('response.status')
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
        print('use audio')
        pc.addTrack(audio.audio)
    else:
        try:
            pc.addTrack(webcam.audio)
        except:
            pass

    offer: RTCSessionDescription = await pc.createOffer()
    await pc.setLocalDescription(offer)

    remote_sdp: Optional[str] = await send_offer(pc, WHIP_SERVER_URL)
    if not remote_sdp:
        return
    await apply_answer(pc, remote_sdp)

    return pc

# pionのwhip-whep exampleはDELETEに対応していないので使わない
async def on_shutdown(pc: RTCPeerConnection) -> None:
    print('on_shutdown')

    response = await call_api('post', WHIP_SERVER_URL)
    print(response)

    if pc:
        await pc.close()


async def create_whip_connection() -> Optional[RTCPeerConnection]:
    pc = await create_peer_connection()
    return pc

async def run():
    # try:
    #     aiortc_main_task = asyncio.create_task(aiortc_whip_main())
    # except Exception as e:
    #     print(e)
    #     aiortc_main_task.cancel()
    #     await aiortc_main_task

    pc = None
    try:
        pc = await create_whip_connection()
    except Exception as e:
        print(f'Exception: {e}')
        await on_shutdown(pc)

    try:
        await asyncio.Event().wait()
    except Exception as e:
        print(f'Exception: {e}')
    finally:
        await on_shutdown(pc)

if __name__ == '__main__':
    asyncio.run(run())
