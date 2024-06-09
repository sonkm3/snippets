FROM debian:buster
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        cmake \
        build-essential \
        binutils-arm-none-eabi \
        gcc-arm-none-eabi \
        libnewlib-dev \
        libstdc++-arm-none-eabi-newlib \
        git \
        ca-certificates \
        python3 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /raspberrypi-pico

RUN git clone -b pico https://github.com/raspberrypi/micropython.git

WORKDIR /raspberrypi-pico/micropython/
RUN git submodule update --init -- lib/pico-sdk

WORKDIR /raspberrypi-pico/micropython/lib/pico-sdk
RUN git submodule update --init

WORKDIR /raspberrypi-pico/micropython/
RUN make -C mpy-cross

WORKDIR /raspberrypi-pico/micropython/ports/rp2
RUN make

# RUN picotool info -a build/firmware.uf2
