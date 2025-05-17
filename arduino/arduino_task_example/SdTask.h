#include "M5Atom.h"

#define MAX_MAPPINGS 2
#define MAX_MESSAGE_LENGTH 128
#define FLUSH_INTERVAL_MSEC 1000*10
#define FLUSH_INTERVAL_LINES 10

namespace sdTask{
    void sdCardWriteTask(void *pvParameters);

    typedef struct {
        QueueHandle_t xQueue;
        char filename[32];
    } QueueFileMapping;


    typedef struct {
        int numberOfMappings;
        QueueFileMapping mappings[MAX_MAPPINGS];
    } TaskArgument;
}