import asyncio
from asyncio import Future
from dataclasses import dataclass
import fractions
import functools
import json
import logging
import platform
from typing import Optional, Tuple
from urllib.parse import urljoin

import aiohttp
from aiohttp.client import ClientResponse
from aiohttp import web
from aiortc import RTCConfiguration, RTCIceServer, RTCPeerConnection, RTCSessionDescription
from aiortc.mediastreams import AudioStreamTrack, MediaStreamTrack, VideoStreamTrack
from aiortc.contrib.media import MediaPlayer, MediaRelay
from av import VideoFrame
from PIL import Image, ImageDraw, ImageFont


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


ICE_SERVER_LIST = [RTCIceServer('stun:stun.l.google.com:19302'),]


room_dict = {}


class DefaultStreamTrack(VideoStreamTrack):
    def __init__(self):
        super().__init__()
        height, width = 480, 640

        self.canvas = Image.new("RGB", (width, height), color='white')
        draw = ImageDraw.Draw(self.canvas)

    def _get_image(self, time_base: fractions.Fraction):
        return self.canvas

    async def recv(self):
        pts, time_base = await self.next_timestamp()

        frame = VideoFrame.from_image(self._get_image(time_base))
        frame.pts = pts
        frame.time_base = time_base
        self.counter += 1
        return frame


def get_default_track() -> MediaStreamTrack:
    # default_audio_track: Optional[AudioStreamTrack]
    default_video_track: Optional[VideoStreamTrack]

    def _get_default_track() -> MediaStreamTrack:
        # default_audio_track = locals().get('default_audio_track', FlagVideoStreamTrack())
        default_video_track = locals().get('default_video_track', FlagVideoStreamTrack())
    return _get_default_track


@dataclass
class Relay:
    track_id: str
    relay: MediaRelay

# dataclass?
class Perticipent:
    pc: RTCPeerConnection
    def __init__(self, pc: RTCPeerConnection):
        self.pc = pc

# dataclass?
class Viewer(Perticipent):
    pass

# dataclass?
class BroadCaster(Perticipent):
    relay_dict: dict[MediaRelay]
    def __init__(self, pc:RTCPeerConnection):
        super().__init__()
        self.relaydict = {}


class Room:
    def __init__(self, room_id: int, dummy_video_track: VideoStreamTrack):
        self.room_id = room_id
        self.broadcaster_list: BroadCaster = []
        self.viewer_list: Viewer = []
        self.relay_list: MediaRelay = []

        self.dummy_video_track: VideoStreamTrack = dummy_video_track

        self.default_video_relay: MediaRelay = MediaRelay()
        self.default_video_relay.subscribe(self.dummy_video_track)

    def broadcaster_join(self, new_broadcaster: BroadCaster):
        self.broadcaster_list.append(new_broadcaster)

    def viewer_join(self, new_viewer: Viewer):
        self.viewer_list.append(new_viewer)
        # subscribe?

    def broadcaster_leave(self, leaving_broadcaster: BroadCaster):
        self.broadcaster_list = [broadcaster for broadcaster in self.broadcaster_list if broadcaster != leaving_broadcaster]
        # notify to subscrivers?

    def viewer_leave(self, leaving_viewer: BroadCaster):
        self.viewer_list = [viewer for viewer in self.viewer_list if viewer != leaving_viewer]

    def track_start(self, track: MediaStreamTrack):
        relay: MediaRelay = MediaRelay()
        relay.subscribe(track)
        self.relay_list.append(Relay(track_id=track.id, relay=relay))

    def get_default_video_track(self) -> VideoStreamTrack:
        return self.default_video_relay

def handle_root(request: web.Request) -> web.StreamResponse:
    return web.Response(text='hello')


class WhipView(web.View):
    async def post(self) -> web.StreamResponse:
        pc: RTCPeerConnection = RTCPeerConnection(RTCConfiguration(ICE_SERVER_LIST))
        broadcaster: BroadCaster

        @pc.on('track')
        def on_track(track):
            if track.kind == 'video':
                pc.addTrack(track.video)
            elif track.kind == 'audio':
                pc.addTrack(track.audio)

            broadcaster.track_start(track)

            @track.on("ended")
            async def on_ended():
                print(f'track: {track} ended')
                pass

        room_id = self.request.match_info.get('room_id')
        data = await self.request.post()

        if self.request.headers.get('Content-Type') != 'application/sdp':
            raise

        room: Room = room_dict.get(room_id, Room(room_id, get_default_track()))

        remote_sdp = data

        await pc.setRemoteDescription(RTCSessionDescription(sdp=remote_sdp, type='answer'))

        broadcaster = BroadCaster(pc)
        room.broadcaster_join(broadcaster)

        answer = await pc.createAnswer()

        return web.Response(body=answer, content_type='application/sdp')


    async def delete(self) -> web.StreamResponse:
        room_id = self.request.match_info.get('room_id')
        return web.json_response(
            {
                'method': self.request.method,
                'args': dict(self.request.rel_url.query),
                'headers': dict(self.request.headers),
                'room_id': room_id,
            },
            dumps=functools.partial(json.dumps, indent=4),
        )

class WhepView(web.View):
    async def post(self) -> web.StreamResponse:
        pc: RTCPeerConnection = RTCPeerConnection(RTCConfiguration(ICE_SERVER_LIST))
        viewer: Viewer

        room_id = self.request.match_info.get('room_id')
        data = await self.request.post()

        if self.request.headers.get('Content-Type') != 'application/sdp':
            raise

        room: Room = room_dict.get(room_id, Room(room_id, get_default_track()))

        remote_sdp = data

        pc.addTransceiver(room.get_default_video_track(), direction='sendonly')

        await pc.setRemoteDescription(RTCSessionDescription(sdp=remote_sdp, type='answer'))
        answer = await pc.createAnswer()

        viewer = Viewer(pc)
        room.viewer_join(viewer)

        return web.Response(body=answer, content_type='application/sdp')


app = web.Application()

app.add_routes([
    web.get('/', handle_root),
    web.post(r'/whip/{room_id:\d+}', WhipView),
    web.delete(r'/whip/{room_id:\d+}', WhipView),
    web.post(r'/whep/{room_id:\d+}', WhepView)
    ])

if __name__ == '__main__':
    web.run_app(app)
