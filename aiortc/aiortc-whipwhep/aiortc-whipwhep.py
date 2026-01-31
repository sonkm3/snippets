from dataclasses import dataclass
import fractions
import functools
import json
import logging
from typing import Optional, Tuple


from aiohttp import web
from aiortc import RTCConfiguration, RTCIceServer, RTCPeerConnection, RTCSessionDescription
from aiortc.mediastreams import AudioStreamTrack, MediaStreamTrack, VideoStreamTrack
from aiortc.contrib.media import MediaPlayer, MediaRelay
from av import AudioFrame, VideoFrame
from PIL import Image, ImageDraw, ImageFont


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


ICE_SERVER_LIST = [RTCIceServer('stun:stun.l.google.com:19302'),]


room_dict = {}


class DummyVideoStreamTrack(VideoStreamTrack):
    def __init__(self):
        super().__init__()
        height, width = 480, 640

        self.canvas = Image.new("RGB", (width, height), color='white')
        draw = ImageDraw.Draw(self.canvas)
        # todo  draw some texts

    def _get_image(self, time_base: fractions.Fraction):
        return self.canvas
        # return self.canvases[time_base % 30]

    def _get_video_frame(self, time_base):
        return VideoFrame.from_image(self._get_image(time_base))

    async def recv(self):
        pts, time_base = await self.next_timestamp()

        frame: VideoFrame = self._get_video_frame(time_base)

        frame.pts = pts
        frame.time_base = time_base
        self.counter += 1
        return frame

# create silent audio track
# how to create silent audiotrack without numpy
# https://github.com/PyAV-Org/PyAV/issues/523#issuecomment-492186517
# how to create silent audiotrack with numpy
# https://github.com/PyAV-Org/PyAV/issues/523#issuecomment-1301823518
class DummyAudioStreamTrack(AudioStreamTrack):
    def __init__(self):
        super().__init__()
        self.frame = AudioFrame(samples=1152)
        self.frame.pts = None
        self.frame.rate = 48000

    def _get_audio_frame(self):
        return self.frame

    async def recv(self):
        pts, time_base = await self.next_timestamp()

        frame: AudioFrame = self._get_audio_frame()

        frame.pts = pts
        frame.time_base = time_base
        self.counter += 1
        return frame


def get_dummy_track() -> MediaStreamTrack:
    dummy_audio_track: Optional[AudioStreamTrack]
    dummy_video_track: Optional[VideoStreamTrack]

    def _get_dummy_track() -> MediaStreamTrack:
        dummy_audio_track = locals().get('dummy_audio_track', DummyAudioStreamTrack())
        dummy_video_track = locals().get('dummy_video_track', DummyVideoStreamTrack())
        return dummy_audio_track, dummy_video_track
    return _get_dummy_track


class Perticipent:
    pc: RTCPeerConnection
    def __init__(self, pc: RTCPeerConnection):
        self.pc = pc


class Viewer(Perticipent):
    pass


class BroadCaster(Perticipent):
    pass


# todo  MediaRelayはtrackの差し替えに対応していないのでtrack差し替えに対応したMediaRelayを継承して作る必要がある
# track差し替えできる実装かどうか疑問なので再度確認する

class Relay:
    def __init__(self, audio_track: AudioStreamTrack, video_track: VideoStreamTrack, broadcaster: BroadCaster, viewer: Viewer):
        self.audio_track_id: str = audio_track.id
        self.video_track_id: str = video_track.id

        self.audio_relay: MediaRelay = MediaRelay()
        self.video_relay: MediaRelay = MediaRelay()
        self.audio_relay.subscribe(audio_track)
        self.video_relay.subscribe(video_track)

        self.broadcaster: Optional[BroadCaster] = broadcaster
        self.viewer: Optional[Viewer] = viewer

# todo  add method to change MediaRelay's reference from dummy to broadcaster (or viceversa)
class Room:
    def __init__(self, room_id: int, dummy_audio_track: AudioStreamTrack, dummy_video_track: VideoStreamTrack):
        self.room_id = room_id
        self.broadcaster_list: BroadCaster = []
        self.viewer_list: Viewer = []
        self.relay_list: MediaRelay = [] # todo  Relayクラスに変更 <- できてない

        # we can use different dummy tracks for each Room
        self.dummy_audio_track: VideoStreamTrack = dummy_audio_track
        self.dummy_video_track: VideoStreamTrack = dummy_video_track

    def broadcaster_join(self, new_broadcaster: BroadCaster):
        self.broadcaster_list.append(new_broadcaster)
        # dummy_trackから配信者のRelayへの付け替え処理が入っていない

    def viewer_join(self, new_viewer: Viewer):
        self.viewer_list.append(new_viewer)

        # ここは実装できてない
        # if broadcaster exists, broadcaster will be themselves(subscrive existing stream)
        broadcaster = None

        relay = Relay(self.dummy_audio_track, self.dummy_video_track, broadcaster, new_viewer)
        self.relay_list.append(relay)

    def broadcaster_leave(self, leaving_broadcaster: BroadCaster):
        self.broadcaster_list = [broadcaster for broadcaster in self.broadcaster_list if broadcaster != leaving_broadcaster]
        # notify to subscrivers?
        # relay_listのソースをダミーからbroadcasterのtrackに切り替える

    def viewer_leave(self, leaving_viewer: BroadCaster):
        self.viewer_list = [viewer for viewer in self.viewer_list if viewer != leaving_viewer]
        self.relay_list = [relay for relay in self.relay_list if relay.viewer != leaving_viewer]

    def track_start(self, track: MediaStreamTrack):
        relay: MediaRelay = MediaRelay() # todo  Relayクラスの修正に対応する
        relay.subscribe(track)
        self.relay_list.append(Relay(track_id=track.id, relay=relay))

    # MediaRelayの使い方間違ってるかも？(元の実装はViewerごとにRelayを用意していた気がするしそちらが正解では？)
    # これいらんかも？
    def get_default_video_relay(self) -> VideoStreamTrack:
        return self.default_video_relay

def handle_root(request: web.Request) -> web.StreamResponse:
    return web.Response(text='hello')


class WhipView(web.View):
    async def post(self) -> web.StreamResponse:
        pc: RTCPeerConnection = RTCPeerConnection(RTCConfiguration(ICE_SERVER_LIST))
        broadcaster: BroadCaster

        # 以下のようにdecolatorではなくメソッドで関数オブジェクトを渡すとRTCPeerConnectionのインスタンス化を後回しにできる(HTTP APIとRTC処理は分けたほうが良いとして)
        # ee.on('data', data_handler) <- pc.on('data', data_handler)
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

        room: Room = room_dict.get(room_id, Room(room_id, get_dummy_track()))

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

        room: Room = room_dict.get(room_id, Room(room_id, get_dummy_track()))

        remote_sdp = data

        pc.addTransceiver(room.get_default_video_relay(), direction='sendonly')

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
