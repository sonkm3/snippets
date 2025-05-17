#include "M5Atom.h"

#include "SdTask.h"

namespace sdTask{
  void sdCardWriteTask(void *pvParameters) {
    TaskArgument *args = (TaskArgument *)pvParameters;
    int numberOfMappings = args->numberOfMappings;
    QueueFileMapping *mappings = args->mappings;

    // char message[64]; // キューから受信するメッセージを格納するバッファ(todo  バッファとしてメモリを確保するようにする)
    char *receivedMessage = (char *)malloc(MAX_MESSAGE_LENGTH * sizeof(char));

    uint32_t lastFlush[MAX_MAPPINGS];
    int bufferedLines[MAX_MAPPINGS];

    for (int i = 0; i < MAX_MAPPINGS; i++){
      lastFlush[i] = millis();
      bufferedLines[i] = 0;
    }

    Serial.printf("キュー数: %d\r\n", numberOfMappings);
    for (int i = 0; i < numberOfMappings; i++) {
        Serial.printf("ファイル名 %d: %s\r\n", i, mappings[i].filename);
    }

    //  todo: ファイルをオープンする
    //  todo:  ファイルハンドルのリストを用意する

    while (true) {
        for (int i = 0; i < numberOfMappings; i++) {
            if (xQueueReceive(mappings[i].xQueue, receivedMessage, pdMS_TO_TICKS(100)) == pdTRUE) {
                //  todo: 実際にファイルへ書き込む処理を実装
                Serial.printf("ファイル %s に書き込み: %s\r\n", mappings[i].filename, receivedMessage);

                bufferedLines[i]++;
                if (bufferedLines[i] >= FLUSH_INTERVAL_LINES || (millis() - lastFlush[i]) >= FLUSH_INTERVAL_MSEC) {
                    //  todo: 実際にファイルをflushする
                    // logFile.flush();
                    Serial.printf("flush: %i をflush bufferdlines: %i lastFlush diff: %i \r\n", i, bufferedLines[i], (millis() - lastFlush[i]));
                    bufferedLines[i] = 0;
                    lastFlush[i] = millis();
                }
            }
            //  todo: flush処理はここにも必要(キューの更新がされなくなって一定期間経った場合の対応)
        }
        vTaskDelay(pdMS_TO_TICKS(100));
    }
    free(receivedMessage);
  }
}
