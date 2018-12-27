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
// OBJECTS
//------------------------------------------------------------------------------
SdFatSdioEX sd;
File file;

int writeCount = 0;

//------------------------------------------------------------------------------
//  FIFO 
//    The FIFO is used as a shared memory between the FlexCAN::CANListener
//    interface and the SdFat::SdFatSdioEX interface.  The FlexCAN::CANListener
//    interface will be adding CAN frames to the FIFO and the SdFat::SdFatSdioEX
//    interface will be writing FIFO data to the micro SD card.
//------------------------------------------------------------------------------
const size_t BLOCK_SIZE = 32;
const size_t FIFO_SIZE = 32;

// Data block: 32 * 16 bytes = 512 bytes
typedef struct block_t {
    CAN_message_t frame_array[BLOCK_SIZE];
} block_t;

// FIFO: 32 * 512 bytes = 16,384 bytes
block_t fifo[FIFO_SIZE];
size_t fifo_head = 0;
size_t fifo_tail = 0;

// Count of blocks in the FIFO
SEMAPHORE_DECL(fifo_data, 0);

// Count of free blocks in the FIFO
SEMAPHORE_DECL(fifo_space, FIFO_SIZE);


//------------------------------------------------------------------------------
// CANClass
//    The CANClass uses FlexCAN::CANListener as the base class.  The
//    frameHandler callback is used to call our saveFrame method.  This method
//    will buffer a "blocks"-worth of data before moving the data into the FIFO.
//------------------------------------------------------------------------------
class CANClass : public CANListener {
  public:
    void saveFrame(CAN_message_t &frame);
    void printFrame(CAN_message_t &frame, int mailbox);
    bool frameHandler(CAN_message_t &frame, int mailbox, uint8_t controller);
    CANClass() : block_head(0) {}

  private:
    block_t block;
    size_t block_head;
};

void CANClass::saveFrame(CAN_message_t &frame)
{
  //Serial.println(F("CANClass: Received CAN Frame"));
  block.frame_array[block_head] = frame;
  if (block_head < (BLOCK_SIZE - 1)) {
    block_head = block_head + 1;
  }
  else {
    if (chSemWaitTimeout(&fifo_space, TIME_IMMEDIATE) != MSG_OK) {
      Serial.println(F("CANClass ERROR: Overrun condition"));    
    }
    //Serial.println(F("CANClass: Saving block to FIFO"));
    fifo[fifo_head] = block;
    chSemSignal(&fifo_data);
    fifo_head = fifo_head < (FIFO_SIZE - 1) ? fifo_head + 1 : 0;
    block_head = 0;
  }
}

void CANClass::printFrame(CAN_message_t &frame, int mailbox)
{
  Serial.print(mailbox);
  Serial.print(" ID: ");
  Serial.print(frame.id, HEX);
  Serial.print(" Data: ");
  for (int c = 0; c < frame.len; c++) 
  {
    Serial.print(frame.buf[c], HEX);
    Serial.write(' ');
  }
  Serial.println();
}

bool CANClass::frameHandler(CAN_message_t &frame, int mailbox, uint8_t controller)
{
    printFrame(frame, mailbox);
    //saveFrame(frame);
    return true;
}

//CANClass CANClass0;
CANClass CANClass1;

//------------------------------------------------------------------------------
//  SETUP
//------------------------------------------------------------------------------
void setup()
{
  Serial.begin(9600);

  // Wait for USB Serial.
  while (!Serial) {}
  Serial.println(F("Setup: Initializing CAN Interface"));

  //Can0.begin(1000000);  
  //Can0.attachObj(&CANClass0);
  Can1.begin(1000000);  
  Can1.attachObj(&CANClass1);
    
  CAN_filter_t allPassFilter;
  allPassFilter.id=0;
  allPassFilter.ext=1;
  allPassFilter.rtr=0;

  for (uint8_t filterNum = 0; filterNum < 16;filterNum++){
    //Can0.setFilter(allPassFilter,filterNum);
    Can1.setFilter(allPassFilter,filterNum); 
  }
  //CANClass0.attachGeneralHandler();
  CANClass1.attachGeneralHandler();

  Serial.println(F("Setup: Initializing SD Card Interface"));
  // Open file and set the date and time
  if (!sd.begin()) {
    Serial.println(F("Setup: SD begin failed."));
    while (true) {}
  }
  if (!file.open("log_file.bin", O_CREAT | O_WRITE | O_TRUNC)) {
    Serial.println(F("Setup: File open failed."));
    while (true) {} 
  }
  //tmElements_t start_time;
  //breakTime(now(), start_time);
  //if (!file.timestamp(T_CREATE, start_time.Year, start_time.Month, start_time.Day, start_time.Hour, start_time.Minute, start_time.Second)) {
  //  Serial.println(F("ERROR: Cannot update file timestamp"));
  //}

  chBegin(0);  // Start kernel - loop() becomes main thread
  while (true) {}  // chBegin() resets stacks and should never return
}


//------------------------------------------------------------------------------
//  LOOP
//------------------------------------------------------------------------------
void loop() {

  /*// SD write loop.
  while (writeCount < 10) {

    Serial.println(F("Loop: Waiting for a block of data"));
    // Wait for next block of data to get loaded into the FIFO
    chSemWait(&fifo_data);

    block_t *block = &fifo[fifo_tail];

    // Write the block of data to the file
    if (512 != file.write(block, 512)) {
        sd.errorHalt("Loop: SD write failed");
    }

    // Release the FIFO block
    chSemSignal(&fifo_space);
    
    Serial.println(F("Loop: Wrote a block of data"));
    // Advance FIFO tail index
    fifo_tail = fifo_tail < (FIFO_SIZE - 1) ? fifo_tail + 1 : 0;
    writeCount = writeCount + 1;
  }
  Serial.println(F("Loop: Exiting"));
  */file.close();  
  while (true) {}
}


/*
//------------------------------------------------------------------------------
//  LOOP
//------------------------------------------------------------------------------
void loop() {

  Serial.println(F("Loop: Runnning...type any character to end"));
    
  // Start thread
  chThdCreateStatic(waThread1, sizeof(waThread1), NORMALPRIO + 1, Thread1, NULL);    
  
  while (!Serial.available()) {}

  Serial.println(F("Loop: Exiting"));
  file.close();  

  while (true) {}
}

//------------------------------------------------------------------------------
// MICRO SD WRITER THREAD
//    Declare a stack with 32 bytes beyond task switch and interrupt needs.
//------------------------------------------------------------------------------
static THD_WORKING_AREA(waThread1, 32);

static THD_FUNCTION(Thread1, arg) {
  (void)arg;

  while (true) {
    Serial.print(F("SDWriter: Waiting for a block of data"));
    // Wait for next block of data to get loaded into the FIFO
    chSemWait(&fifo_data) == MSG_OK

    block_t *block = &fifo[fifo_tail];

    // Write the block of data to the file
    if (512 != file.write(block, 512)) {
        sd.errorHalt("write failed");
    }

    // Release the FIFO block
    chSemSignal(&fifo_space);
    
    Serial.print(F("SDWriter: Wrote a block of data"));
    // Advance FIFO tail index
    fifo_tail = fifo_tail < (FIFO_SIZE - 1) ? fifo_tail + 1 : 0;
  }
}


*/
