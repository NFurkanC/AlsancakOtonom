#include <Servo.h>
#include <SPI.h>
#include <mcp2515.h>

#define maxdeger 1940 //max 2000 oluyor escler 1000-2000 arası calisir
#define mindeger 1060
#define sabitleme_toleransi 130
#define joystick_sensinterval 10
#define joystick_sensivity_multiplier
// Tam manevrada 1 saniyede 180 derece dönmesi hedeflenerek 180/(1000/10)*500
#define joystick_sensivity_multiplier 0.0036

unsigned long currenttime;


int ksayac;
int Kp = 14000, Ki = 13, Kd = 18;

byte sicaklik = 0, akim = 0, lambadeger = 0, arm = 0;
int  derinlik = 0, voltaj = 0;


int anglez = 0;

struct can_frame canSnd;
struct can_frame canMsg;

struct joystick
{
  int jmin = 0;
  int jmax = 0;
  int jmid = 0;
  int pin = 0;
  int value = 0;
};

joystick x1, x2, y1, y2;

MCP2515 mcp2515(8);

float hizBoleni = 1.0;

union ArrayToInteger {
  byte array[2];
  int integer;
} converter;
union ArrayToDouble {
  byte array[4];
  double number;
} doubler;

void setup()
{


  x1.pin = 0;
  y1.pin = 1;
  x2.pin = 3;
  y2.pin = 2;
  x1.jmid = analogRead(x1.pin);
  x2.jmid = analogRead(x2.pin);
  y1.jmid = analogRead(y1.pin);
  y2.jmid = analogRead(y2.pin);
  Serial.begin(115200);
  SPI.begin();
  //joystick_calibration();
  //calibration results will be copied here
  
x1.jmin = 65;
x1.jmid = 496;
x1.jmax = 1023;
y1.jmin = 192;
y1.jmid = 498;
y1.jmax = 794;
x2.jmin = 205;
x2.jmid = 514;
x2.jmax = 757;
y2.jmin = 283;
y2.jmid = 532;
y2.jmax = 813;



  mcp2515.reset();
  mcp2515.setBitrate(CAN_125KBPS, MCP_8MHZ);
  mcp2515.setNormalMode();
  pinMode(7, INPUT_PULLUP);
  pinMode(4, INPUT_PULLUP);
}

void loop()
{
  currenttime = millis();
  arm = digitalRead(7);
  lambadeger = digitalRead(4);

  Serial.print("X1  ");
    Serial.print(x1.value);
    Serial.print("  Y1");
    Serial.print(y1.value);
    Serial.print("  X2");
    Serial.print(x2.value);
    Serial.print("  Y2");
    Serial.println(y2.value);

  Serial.print(anglez);
  Serial.print("*");
  Serial.print(derinlik*10);
  Serial.print("*");
  //*5/1024/0,18
  Serial.print(voltaj*0.0271*1000);
  Serial.print("*");
  Serial.print(sicaklik*1000);
  Serial.print("?");
  
  //kp,ki,kd belirleme kısmı
  if (Serial.available()) {
    agirlikbelirle();
  }

  // Araçtan gelen değerler bölünerek USB Üzerine yazılıyor.
  // Eğer araçtan bir bilgi yukarı gelecek ise bunu Can_ID'si üzerinden belirtmeniz gerekir.
  if (mcp2515.readMessage(&canMsg) == MCP2515::ERROR_OK)
  {

    /*Serial.print(canMsg.can_id, HEX); // print ID
      Serial.print(" ");
      Serial.print(canMsg.can_dlc, HEX); // print DLC
      Serial.print(" ");*/

    for (int i = 0; i < canMsg.can_dlc; i++)  { // print the data
      //Serial.print(canMsg.data[i],HEX);
      //Serial.print(" ");
    }
    if (canMsg.can_id == 0x03)
    {
      for (int i = 0; i < canMsg.can_dlc; i += 2)
      {
        converter.array[1] = canMsg.data[i];
        converter.array[0] = canMsg.data[i + 1];
        if (i == 0)
        
          anglez = converter.integer;
        
        else if (i == 2)
           voltaj = converter.integer;

        else if (i == 4)
          derinlik = converter.integer;
        
        else if (i == 6){
          akim = canMsg.data[i];
         sicaklik = canMsg.data[i + 1];
        }
      }
    }
  }

  // analogRead 0-1023 arasında okuma yapar, burada esc değerleri olan 1000-2000 arasına eşitleniyor.
  // Herhangi bir joystick değerini 3000'den çıkarmak, joystick eksenini ters çevirme anlamına gelir.
  x1.value = 3000 - (map(analogRead(x1.pin), x1.jmin, x1.jmax, 0, 1000) + 1000);
  y1.value = 3000 - (map(analogRead(y1.pin), y1.jmin, y1.jmax, 0, 1000) + 1000);
  x2.value = map(analogRead(x2.pin), x2.jmin, x2.jmax, 0, 1000) + 1000;
  y2.value = map(analogRead(y2.pin), y2.jmin, y2.jmax, 0, 1000) + 1000;

  // Joystick değerlerini merkezi değiştirmeden bölme işlemleri
  x1.value = 1500 + (x1.value - 1500) / hizBoleni;
  y1.value = 1500 + (y1.value - 1500) / hizBoleni;
  x2.value = 1500 + (x2.value - 1500) / hizBoleni;
  y2.value = 1500 + (y2.value - 1500) / hizBoleni;


  if (x1.value > maxdeger) x1.value = maxdeger;
  if (y1.value > maxdeger) y1.value = maxdeger;
  if (x2.value > maxdeger) x2.value = maxdeger;
  if (y2.value > maxdeger) y2.value = maxdeger;

  if (x1.value < mindeger) x1.value = mindeger;
  if (y1.value < mindeger)y1.value = mindeger;
  if (x2.value < mindeger) x2.value = mindeger;
  if (y2.value < mindeger)y2.value = mindeger;

  // joystick'ler belli bi toleransla ortadayken 1500'e sabitliyoruz
  if (x1.value < 1500 + sabitleme_toleransi / hizBoleni && x1.value > 1500 - sabitleme_toleransi / hizBoleni)
    x1.value = 1500;
  if (y1.value < 1500 + sabitleme_toleransi / hizBoleni && y1.value > 1500 - sabitleme_toleransi / hizBoleni)
    y1.value = 1500;
  if (x2.value < 1500 + sabitleme_toleransi / hizBoleni && x2.value > 1500 - sabitleme_toleransi / hizBoleni)
    x2.value = 1500;
  if (y2.value < 1500 + sabitleme_toleransi / hizBoleni && y2.value > 1500 - sabitleme_toleransi / hizBoleni)
    y2.value = 1500;

  // Joystick degerleri 8 byte'a siralanip yollaniyor
  canSnd.can_id = 0x02;
  canSnd.can_dlc = 8;
  canSnd.data[0] = highByte(x1.value);
  canSnd.data[1] = lowByte(x1.value);
  canSnd.data[2] = highByte(y1.value);
  canSnd.data[3] = lowByte(y1.value);
  canSnd.data[4] = highByte(x2.value);
  canSnd.data[5] = lowByte(x2.value);
  canSnd.data[6] = highByte(y2.value);
  canSnd.data[7] = lowByte(y2.value);
  mcp2515.sendMessage(&canSnd);
  delay(20);
  canSnd.can_id = 0x04;
  canSnd.can_dlc = 1;
  canSnd.data[0] = lambadeger;
  mcp2515.sendMessage(&canSnd);
  delay(20);

  //Serial.println(analogRead(y2.pin));
  // q-w-e-r her degerin bilgisayardan ayirt edilmesi icin ayri kodlar



}
void agirlikbelirle() {
  String Kpstring = "";
  String Kistring = "";
  String Kdstring = "";
  String rxString = "";
  String strArr[3];
  //Keep looping until there is something in the buffer.
  while (Serial.available()) {
    //Delay to allow byte to arrive in input buffer.
    delay(2);
    //Read a single character from the buffer.
    char ch = Serial.read();
    //Append that single character to a string.
    rxString += ch;
  }
  int stringStart = 0;
  int arrayIndex = 0;
  for (int i = 0; i  < rxString.length(); i++) {
    //Get character and check if it's our "special" character.
    if (rxString.charAt(i) == ',') {
      //Clear previous values from array.
      strArr[arrayIndex] = "";
      //Save substring into array.
      strArr[arrayIndex] = rxString.substring(stringStart, i);
      //Set new string starting point.
      stringStart = (i + 1);
      arrayIndex++;
    }
    //Put values from the array into the variables.
    Kpstring = strArr[0];
    Kistring = strArr[1];
    Kdstring = strArr[2];
    //Convert string to int.
    Kp = Kpstring.toInt();
    Ki = Kistring.toInt();
    Kd = Kdstring.toInt();
  }
}
void joystick_calibration() {
  Serial.print("Calibration Starter");
  int calibration_constant = 30;
  int previous_value;
  int cal = 0;
  x1.jmin = x1.jmid;
  y1.jmin = y1.jmid;
  x2.jmin = x2.jmid;
  y2.jmin = y2.jmid;
  while (cal < calibration_constant * 8 ) {
    if (cal < calibration_constant) {
      Serial.print(previous_value);
      Serial.print("Minvalue = ");
      Serial.print(x1.jmin);
      Serial.println("Calibrating X1");
      previous_value = analogRead(x1.pin);
      if (previous_value < x1.jmid - 50) {
        if (analogRead(x1.pin) < x1.jmin) x1.jmin = previous_value;
        delay(2);
        if (previous_value < x1.jmin + 5) cal++;
      }
    }
    else if (cal < calibration_constant * 2) {
      Serial.print(previous_value);
      Serial.print("Maxvalue = ");
      Serial.print(x1.jmax);
      Serial.println("Calibrating X1");
      previous_value = analogRead(x1.pin);
      if (previous_value > x1.jmid + 50) {
        if (analogRead(x1.pin) > x1.jmax) x1.jmax = previous_value;
        delay(2);
        if (previous_value > x1.jmax - 5) cal++;
      }
    }
    else if (cal < calibration_constant * 3) {
      Serial.print(previous_value);
      Serial.print("Minvalue = ");
      Serial.print(y1.jmin);
      Serial.println("Calibrating Y1");
      previous_value = analogRead(y1.pin);
      if (previous_value < y1.jmid - 50) {
        if (analogRead(y1.pin) < y1.jmin) y1.jmin = previous_value;
        delay(2);
        if (previous_value < y1.jmin + 5) cal++;
      }
    }
    else if (cal < calibration_constant * 4) {
      Serial.print(previous_value);
      Serial.print("Maxvalue = ");
      Serial.print(y1.jmax);
      Serial.println("Calibrating Y1");
      previous_value = analogRead(y1.pin);
      if (previous_value > y1.jmid + 50) {
        if (analogRead(y1.pin) > y1.jmax) y1.jmax = previous_value;
        delay(2);
        if (previous_value > y1.jmax - 5) cal++;
      }
    }
    else if (cal < calibration_constant * 5) {
      Serial.print(previous_value);
      Serial.print("Minvalue = ");
      Serial.print(x2.jmin);
      Serial.println("Calibrating x2");
      previous_value = analogRead(x2.pin);
      if (previous_value < x2.jmid - 50) {
        if (analogRead(x2.pin) < x2.jmin) x2.jmin = previous_value;
        delay(2);
        if (previous_value < x2.jmin + 5) cal++;
      }
    }
    else if (cal < calibration_constant * 6) {
      Serial.print(previous_value);
      Serial.print("Maxvalue = ");
      Serial.print(x2.jmax);
      Serial.println("Calibrating x2");
      previous_value = analogRead(x2.pin);
      if (previous_value > x2.jmid + 50) {
        if (analogRead(x2.pin) > x2.jmax) x2.jmax = previous_value;
        delay(2);
        if (previous_value > x2.jmax - 5) cal++;
      }
    }
    else if (cal < calibration_constant * 7) {
      Serial.print(previous_value);
      Serial.print("Minvalue = ");
      Serial.print(y2.jmin);
      Serial.println("Calibrating Y2");
      previous_value = analogRead(y2.pin);
      if (previous_value < y2.jmid - 50) {
        if (analogRead(y2.pin) < y2.jmin) y2.jmin = previous_value;
        delay(2);
        if (previous_value < y2.jmin + 5) cal++;
      }
    }
    else if (cal < calibration_constant * 8) {
      Serial.print(previous_value);
      Serial.print("Maxvalue = ");
      Serial.print(y2.jmax);
      Serial.println("Calibrating y2");
      previous_value = analogRead(y2.pin);
      if (previous_value > y2.jmid + 50) {
        if (analogRead(y2.pin) > y2.jmax) y2.jmax = previous_value;
        delay(2);
        if (previous_value > y2.jmax - 5) cal++;
      }
    }

  }
  Serial.print("x1.jmin = ");
  Serial.println(x1.jmin);
  Serial.print("x1.jmid = ");
  Serial.println(x1.jmid);
  Serial.print("x1.jmax = ");
  Serial.println(x1.jmax);

  Serial.print("y1.jmin = ");
  Serial.println(y1.jmin);
  Serial.print("y1.jmid = ");
  Serial.println(y1.jmid);
  Serial.print("y1.jmax = ");
  Serial.println(y1.jmax);

  Serial.print("x2.jmin = ");
  Serial.println(x2.jmin);
  Serial.print("x2.jmid = ");
  Serial.println(x2.jmid);
  Serial.print("x2.jmax = ");
  Serial.println(x2.jmax);

  Serial.print("y2.jmin = ");
  Serial.println(y2.jmin);
  Serial.print("y2.jmid = ");
  Serial.println(y2.jmid);
  Serial.print("y2.jmax = ");
  Serial.println(y2.jmax);
  delay(10000);
}
