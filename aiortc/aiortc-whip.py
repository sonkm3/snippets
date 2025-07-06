
import asyncio

import aiohttp
from aiortc import RTCConfiguration, RTCIceServer, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer


whip_server_url: str = 'http://localhost:8080/whip'
ice_server_list = [RTCIceServer('stun:stun.l.google.com:19302'),]


# todo OSごとの対応はここで切り分ける
def get_tracks():
    options: dict = {'framerate': '30', 'video_size': '640x480'}
    webcam: MediaPlayer = MediaPlayer('default:none', format='avfoundation', options=options)
    return webcam

async def send_offer(pc: RTCPeerConnection, url: str):
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
    pc: RTCPeerConnection = RTCPeerConnection(RTCConfiguration(ice_server_list))
    webcam = get_tracks()
    pc.addTransceiver(webcam.video, direction='sendonly')

    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)

    remote_sdp = await send_offer(pc, whip_server_url)
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
        response = await session.delete(whip_server_url)
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
