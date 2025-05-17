# Arduino(ESP32)でFreeRTOS由来のタスクを生成しキューでメッセージを送信するサンプル

## 背景
- ArduinoでSDカードへの書き込みをタスクとして実装する処理の前段階の実装としてキュー経由でメッセージの送信の実装を試した
- そのためSdTaskなどでSDカードに関連する名前が残っている

## 実装したこと
- タスクの生成
- キューの生成

## 実装していないこと
- SDカードの取り扱い
- メッセージは値渡しのため、長さの制限がある

## 想定する依存ライブラリなど
### Boards Manager
- M5Stack 2.1.4

### 依存ライブラリ
- M5Atom 0.1.3

## ビルド手順
### Arduino IDE
- Arduino IDEから実行

### Arduino CLI
- Arduino CLIから実行
```bash
$ arduino-cli board list
Port                            Protocol Type              Board Name FQBN Core
/dev/cu.usbserial-xxxxx    serial   Serial Port (USB) Unknown

$ arduino-cli compile
$ arduino-cli upload -p /dev/cu.usbserial-xxxxx
```

## 出力されるログ

起動時
```
initialize!!!

キュー数: 2
キュー1へのメッセージ送信成功: ログメッセージ from loop 1 1回目
ファイル名 0: file1.txt
ファイル名 1: file2.txt
ファイル file1.txt に書き込み: ログメッセージ from loop 1 1回目
ファイル file2.txt に書き込み: ログメッセージ from loop 2 1回目
キュー2へのメッセージ送信成功: ログメッセージ from loop 2 1回目
ファイル file1.txt に書き込み: ログメッセージ from loop 1 2回目
キュー1へのメッセージ送信成功: ログメッセージ from loop 1 2回目
ファイル file2.txt に書き込み: ログメッセージ from loop 2 2回目
キュー2へのメッセージ送信成功: ログメッセージ from loop 2 2回目
```

flush処理
```

ファイル file1.txt に書き込み: ログメッセージ from loop 1 19回目
キュー1へのメッセージ送信成功: ログメッセージ from loop 1 19回目
ファイル file2.txt に書き込み: ログメッセージ from loop 2 19回目
キュー2へのメッセージ送信成功: ログメッセージ from loop 2 19回目
ファイル file1.txt に書き込み: ログメッセージ from loop 1 20回目
flush: 0 をflush bufferdlines: 10 lastFlush diff: 10200
キュー1へのメッセージ送信成功: ログメッセージ from loop 1 20回目
ファイル file2.txt に書き込み: ログメッセージ from loop 2 20回目
flush: 1 をflush bufferdlines: 10 lastFlush diff: 10201 
キュー2へのメッセージ送信成功: ログメッセージ from loop 2 20回目
ファイル file1.txt に書き込み: ログメッセージ from loop 1 21回目
キュー1へのメッセージ送信成功: ログメッセージ from loop 1 21回目
ファイル file2.txt に書き込み: ログメッセージ from loop 2 21回目
キュー2へのメッセージ送信成功: ログメッセージ from loop 2 21回目

```
