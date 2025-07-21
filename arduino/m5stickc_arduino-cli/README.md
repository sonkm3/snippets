# arduino-cliの動作確認用

## 背景
- arduino-cliの動作確認をしたかった

## 実装したこと
- M5StickCでバッテリー電圧を表示

## 実装していないこと
- 

## 想定する依存ライブラリなど
### Boards Manager
- M5Stack 3.2.2

### 依存ライブラリ
- M5StickC 0.3.0

## ビルド手順
### Arduino IDE
- Arduino IDEから実行

### Arduino CLI
#### coreのインストール
```bash
$ arduino-cli core install m5stack:esp32
```

#### アップロード
```bash
$ arduino-cli board list
Port                            Protocol Type              Board Name FQBN Core
/dev/cu.usbserial-xxxxx    serial   Serial Port (USB) Unknown

$ arduino-cli compile
$ arduino-cli upload -p /dev/cu.usbserial-xxxxx
```

#### make
##### boardをattach
```bash
$ arduino-cli board attach -p /dev/cu.usbserial-xxxxx
```

##### make
```bash
$ make
```

```bash
$ make monitor
```