#include "M5Atom.h"

#include "SdTask.h"


// loop実行時に前回の状態を保持するためのグローバル変数
bool running = true;
int loopCounter = 0;
char message[MAX_MESSAGE_LENGTH];

// setupからloopへ共有するためのタスク構造体(タスクへも共有される)
static sdTask::TaskArgument taskArgs;

// キューの設定
#define QUEUE_COUNT 5

void setup() {
    M5.begin();

    Serial.println("\r\ninitialize!!!\r\n");

    // タスクとキューのマッピング構造体を定義
    taskArgs.numberOfMappings = 2;

    taskArgs.mappings[0].xQueue = xQueueCreate(QUEUE_COUNT, sizeof(char[MAX_MESSAGE_LENGTH]));
    strcpy(taskArgs.mappings[0].filename, "file1.txt");

    taskArgs.mappings[1].xQueue = xQueueCreate(QUEUE_COUNT, sizeof(char[MAX_MESSAGE_LENGTH]));
    strcpy(taskArgs.mappings[1].filename, "file2.txt");

    BaseType_t xReturned;
    TaskHandle_t xHandle = NULL;
    xReturned = xTaskCreate(
        sdTask::sdCardWriteTask, // タスク関数
        "SDWriteTaskMultiQueue", // タスク名
        2048, // スタックサイズ
        (void *)&taskArgs, // 構造体のアドレスを渡す
        5, // 優先度
        &xHandle // タスクハンドル
    );
}

void loop() {
    M5.update();
    if (M5.Btn.wasPressed()) {
        if (running) {
            running = false;
            Serial.println("Stop");
        } else {
            running = true;
            Serial.println("Restart");
        }
    }

    if (running){
        loopCounter++;

        sprintf(message, "ログメッセージ from loop 1 %d回目", loopCounter);
        if (xQueueSend(taskArgs.mappings[0].xQueue, message, pdMS_TO_TICKS(10)) == pdTRUE) {
            Serial.printf("キュー1へのメッセージ送信成功: %s\r\n", message);
        } else {
            Serial.println("キュー1へのメッセージの送信に失敗しました");
        }

        sprintf(message, "ログメッセージ from loop 2 %d回目", loopCounter);
        if (xQueueSend(taskArgs.mappings[1].xQueue, message, pdMS_TO_TICKS(10)) == pdTRUE) {
            Serial.printf("キュー2へのメッセージ送信成功: %s\r\n", message);
        } else {
            Serial.println("キュー2へのメッセージの送信に失敗しました");
        }
    }
    delay(1000);
}