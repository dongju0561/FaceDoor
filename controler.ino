#include<SPI.h>

#define OBJECT  0xA0
#define SENSOR  0xA1
#define Step 6
#define Dir  5
#define sw1 2
#define sw2 3

const int chipSelectPin  = 10;
unsigned char Timer1_Flag = 0;
int  iOBJECT, iSENSOR;  // 부호 2byte 온도 저장 변수 
int cnt = 0;
float temp = 0 , object_temp = 0, max_temp = 0;
int flag = HIGH;
char state = 0;
int x=0;
int y=0;



void setup() {

  digitalWrite(chipSelectPin , HIGH);
  pinMode(chipSelectPin , OUTPUT);
  SPI.setDataMode(SPI_MODE3);
  SPI.setClockDivider(SPI_CLOCK_DIV16);
  SPI.setBitOrder(MSBFIRST);
  SPI.begin();

  delay(500);
  Timer1_Init();
  Serial.begin(9600);
  interrupts();

  pinMode(Step,OUTPUT);
  pinMode(Dir,OUTPUT);
  pinMode(sw1,INPUT);
  attachInterrupt(0,openSw,CHANGE);
  pinMode(sw2,INPUT);
  attachInterrupt(1,closeSw,CHANGE);
}

void loop() {
  float temp = temp_capture();

  if(temp > 20&&temp < 37.5){
      Serial.print("[open]");
      openDoor();
      delay(3000);
      Serial.print("[close]");
      closeDoor();
      temp  = 0;
  }
}

int SPI_COMMAND(unsigned char cCMD)
{
    unsigned char T_high_byte, T_low_byte;
    digitalWrite(chipSelectPin , LOW);
    delayMicroseconds(10);
    SPI.transfer(cCMD);
    delayMicroseconds(10);    
    T_low_byte = SPI.transfer(0x22);
    delayMicroseconds(10);
    T_high_byte = SPI.transfer(0x22);
    delayMicroseconds(10);
    digitalWrite(chipSelectPin , HIGH);
    
    return (T_high_byte<<8 | T_low_byte);
}

ISR(TIMER1_OVF_vect){
  TCNT1 = 34286;
  Timer1_Flag = 1;
}

void Timer1_Init(void){
  TCCR1A = 0;
  TCCR1B = 0;
  TCNT1 = 34286;
  TCCR1B |= (1 << CS12);
  TIMSK1 |= (1 << TOIE1);
}

float temp_capture(){
  
  if(Timer1_Flag){
    Timer1_Flag = 0;
    iOBJECT = SPI_COMMAND(OBJECT);
    delayMicroseconds(10);
    iSENSOR = SPI_COMMAND(SENSOR);
    float temp_cap = float(iOBJECT)/100;
    if(temp_cap > 30 && temp_cap <40){
      cnt++;
      if(max_temp < temp_cap){
        max_temp = temp_cap;
      }
    }

    if(cnt == 5){
      Serial.println(max_temp);
      return max_temp;
      Serial.println("hi");
    }
    delay(10);
   }
}

void openDoor(){
  digitalWrite( Dir   , LOW);   //open
     for ( int i = 0; i < 10000; i++)
     {
         digitalWrite( Step ,flag);
         delay(1);
         flag = !flag;
         if(x == 1)
         {
           //x = 0;
           break;
         }        
     }
}

void closeDoor(){
  digitalWrite( Dir   , HIGH);   //close
     for ( int i = 0; i < 10000; i++)
     {
         digitalWrite( Step  , flag);
         delay(1);
         flag = !flag;
         if(y == 1)
          break;
     }
}

void openSw(){
  x = digitalRead(sw1);
}

void closeSw(){
  y = digitalRead(sw2);
}
