# Setup

## Raspberry pi

### While using Raspberry pi os bookworm, FFmpeg version does not match to use ALSA

- broken dependencies
	- aiortc requires 14 <= pyav <15
	- pyav 14 supports FFmpeg 7
        - from CHANGELOG
            - pyav 14 drops supports for FFmpeg6
                - https://github.com/PyAV-Org/PyAV/blob/main/CHANGELOG.rst#v1400
            - pyav 13 drops supports for FFmpeg5
                - https://github.com/PyAV-Org/PyAV/blob/main/CHANGELOG.rst#v1300
	    - raspberry pi os bookworm have ffmpeg 5
        ```
        $ ffmpeg --version
        ffmpeg version 5.1.7-0+deb12u1+rpt1 Copyright (c) 2000-2025 the FFmpeg developers
        ```
    - easy way is update raspberry pi os to trixie
        - not sure this FFmpeg7 supports hardware encoder on Raspberry pi
	- update to trixie
		- `https://gist.github.com/jauderho/5f73f16cac28669e56608be14c41006c`
	  - after updating raspberry pi os to debian trixie, FFmpeg got to be 7
        ```
        $ ffmpeg --version
        ffmpeg version 7.1.1-1~+rpt1 Copyright (c) 2000-2025 the FFmpeg developers
        ```

### Install dependencies
```
sudo apt install pkg-config
sudo apt install libavdevice-dev
pip install av==14.4.0 --no-binary av
pip install -r requirements.txt
```


# Run

## Run WHIP/WHEP server using pion example
```
git clone https://github.com/pion/webrtc.git
cd examples/whip-whep
go run main.g
```

## Run aiortc-whip.py
```
python aiortc-whip.py
```


