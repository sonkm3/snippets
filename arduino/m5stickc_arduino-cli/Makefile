default: all

all: flash

build:
	arduino-cli compile

upload:
	arduino-cli upload

flash: build
	$(MAKE) upload

monitor:
	arduino-cli monitor

.PHONY: build upload flash all
