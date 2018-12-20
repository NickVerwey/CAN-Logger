// http://www.chibios.org/dokuwiki/doku.php?id=chibios:book:start 
// https://github.com/greiman/ChRt
// https://github.com/greiman/SdFat
// https://github.com/collin80/FlexCAN_Library
//
// Data logger based on a FIFO to decouple SD write latency from data
// acquisition timing.
//
// The FIFO uses two semaphores to synchronize between tasks.
#include "SdFat.h"
#include "ChRt.h"
#include "FlexCAN.h"

//------------------------------------------------------------------------------
// SD definitions
//------------------------------------------------------------------------------
SdFatSdioEX sd;
File file;
tmElements_t start_time;

//------------------------------------------------------------------------------
// FIFO definitions
//------------------------------------------------------------------------------
const size_t BLOCK_SIZE = 32;
const size_t FIFO_SIZE = 32;

// Data block: 32 * 16 bytes = 512 bytes
typedef struct block_t {
    CAN_message_t can_message_array[BLOCK_SIZE];
} block_t;

// FIFO: 32 * 512 bytes = 16,384 bytes
block_t fifo[FIFO_SIZE];

// FIFO index for record to be written
size_t fifo_tail = 0;

// Global overrun
bool overrun = false;

// Count of blocks in the FIFO
SEMAPHORE_DECL(fifo_data, 0);

// Count of free blocks in the FIFO
SEMAPHORE_DECL(fifo_space, FIFO_SIZE);

//------------------------------------------------------------------------------
// Declare a stack with 32 bytes beyond task switch and interrupt needs.
//------------------------------------------------------------------------------
static THD_WORKING_AREA(waThread1, 32);

static THD_FUNCTION(Thread1, arg) {
  (void)arg;
  
  // FIFO index for record to be filled
  size_t fifo_head = 0;

  systime_t logTimeTicks = chVTGetSystemTime();
  while (true) {
    logTimeTicks += 50;
    chThdSleepUntil(logTimeTicks);

    // Get the next block
    if (chSemWaitTimeout(&fifo_space, TIME_IMMEDIATE) != MSG_OK) {
      
      // Fifo full, indicate missed point
      Serial.print(F("overrun"));    
      while (true) {}
      // continue;
    }

    // Block pointer
    block_t* blk_ptr = &fifo[fifo_head];

    // Generate a block of constant data
    for (int i = 0; i < (int) BLOCK_SIZE; i++) {
        blk_ptr->can_message_array[i].id = 1;
        blk_ptr->can_message_array[i].timestamp = 1;
        blk_ptr->can_message_array[i].flags.extended = 1;
        blk_ptr->can_message_array[i].flags.remote = 1;
        blk_ptr->can_message_array[i].flags.overrun = 1;
        blk_ptr->can_message_array[i].flags.reserved = 1;
        blk_ptr->can_message_array[i].len = 1;
        for (int j = 0; j < 8; j++) {
            blk_ptr->can_message_array[i].buf[j] = 1;
        }
    }

    // Signal new data
    chSemSignal(&fifo_data);
    
    // Advance FIFO head index
    fifo_head = fifo_head < (FIFO_SIZE - 1) ? fifo_head + 1 : 0;
  }
}

//------------------------------------------------------------------------------
void setup() {
  Serial.begin(9600);
  
  // Wait for USB Serial
  while (!Serial) {}
  
  // Start kernel - loop() becomes main thread
  chBegin(0);
  
  // chBegin() resets stacks and should never return
  while (true) {}  
}

//------------------------------------------------------------------------------
void loop() {
  Serial.println(F("type any character to begin"));
  while(!Serial.available()); 

  // Open file and set the date and time
  if (!sd.begin()) {
    Serial.println(F("SD begin failed."));
    while (true) {}
  }
  if (!file.open("data.bin", O_CREAT | O_WRITE | O_TRUNC)) {
    Serial.println(F("file open failed."));
    while (true) {} 
  }
  breakTime(now(), start_time)
  if (!file.timestamp(T_CREATE, start_time.year, start_time.month, start_time.day, start_time.hour, start_time.min, start_time.sec)) {
    error("set create time failed");
  }
  
  // Throw away input.
  while (Serial.read() >= 0);
  Serial.println(F("type any character to end"));
    
  // Start producer thread.
  chThdCreateStatic(waThread1, sizeof(waThread1), NORMALPRIO + 1, Thread1, NULL);    
  
  // SD write loop.
  while (!Serial.available()) {
    
    // Wait for next block of data to get loaded into the FIFO
    chSemWait(&fifo_data);

    block_t* blk = &fifo[fifo_tail];
    if (fifo_tail >= FIFO_SIZE) fifo_tail = 0;

    // Write the block of data to the file
    if (16384 != file.write(blk, 16384)) {
        sd.errorHalt("write failed");
    }

    // Release the FIFO block
    chSemSignal(&fifo_space);
    
    // Advance FIFO tail index
    fifo_tail = fifo_tail < (FIFO_SIZE - 1) ? fifo_tail + 1 : 0;
  }

  // Close file, print stats and stop.
  file.close();
  Serial.println(F("Done"));
  Serial.print(F("Unused Thread1 stack: "));
  Serial.println(chUnusedThreadStack(waThread1, sizeof(waThread1)));
  Serial.print(F("Unused main stack: "));
  Serial.println(chUnusedMainStack());
  while (true) {}
}