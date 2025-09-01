
import asyncio
import platform

import aiohttp
from aiortc import RTCConfiguration, RTCIceServer, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer


WHIP_SERVER_URL: str = 'http://localhost:8080/whip'
ICE_SERVER_LIST = [RTCIceServer('stun:stun.l.google.com:19302'),]
# ICE_SERVER_LIST = [RTCIceServer('stun:stun.l.google.com:19302'),RTCIceServer('stun:stun.cloudflare.com:19302'),]


def get_tracks():
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

async def send_offer(pc: RTCPeerConnection, url: str) -> str:
    headers: dict = {'Content-Type': 'application/sdp'}
    local_sdp = pc.localDescription.sdp

    async with aiohttp.ClientSession() as session:
        try:
            response = await session.post(url, data=local_sdp, headers=headers)
        except aiohttp.ClientError as e:
            print('aiohttp.ClientError')
            return
        if response.status not in (200, 201):
            print('response.status')
            return

        return await response.text()

async def apply_answer(pc: RTCPeerConnection, remote_sdp: str):
        await pc.setRemoteDescription(RTCSessionDescription(sdp=remote_sdp, type='answer'))
        return

async def create_peer_connection():
    pc: RTCPeerConnection = RTCPeerConnection(RTCConfiguration(ICE_SERVER_LIST))
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

    remote_sdp: str = await send_offer(pc, WHIP_SERVER_URL)
    if not remote_sdp:
        return
    await apply_answer(pc, remote_sdp)

    return pc

# pion WHIP-WHEPはDELETEに対応していないので使わない
async def on_shutdown():
    print('on_shutdown')
    pass
    # await pc.close()
    async with aiohttp.ClientSession() as session:
        response = await session.delete(WHIP_SERVER_URL)
        print(f'DELETE request done with status: {response.status}')

async def create_whip_connection():
    # pcを明示的に止めたい
    pc = await create_peer_connection()

async def run():
    # try:
    #     await asyncio.gather(create_whip_connection(), asyncio.Event().wait(),)
    # except Exception as e:
    #     print(f'Exception: {e}')
    # finally:
    #     await on_shutdown()
    await asyncio.gather(create_whip_connection(), asyncio.Event().wait(),)

if __name__ == '__main__':
    asyncio.run(run())
