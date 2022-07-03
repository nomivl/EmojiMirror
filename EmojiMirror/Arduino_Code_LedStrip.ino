#include <Adafruit_NeoPixel.h>
#define PIN 5
#define NUM_LEDS 300
// Parameter 1 = number of pixels in strip
// Parameter 2 = pin number (most are valid)
// Parameter 3 = pixel type flags, add together as needed:
//   NEO_KHZ800  800 KHz bitstream (most NeoPixel products w/WS2812 LEDs)
//   NEO_KHZ400  400 KHz (classic 'v1' (not v2) FLORA pixels, WS2811 drivers)
//   NEO_GRB     Pixels are wired for GRB bitstream (most NeoPixel products)
//   NEO_RGB     Pixels are wired for RGB bitstream (v1 FLORA pixels, not v2)
Adafruit_NeoPixel strip = Adafruit_NeoPixel(NUM_LEDS, PIN, NEO_GRB + NEO_KHZ800);


//variabele voor inkomende emotie
String incomingByte ;

void setup() {
  Serial.begin(9600); //nummer serial moet overeenkomen met nummer in python code
  delay( 1000 ); // power-up safety delay
  
  strip.begin();
  strip.show(); // Initialize all pixels to 'off'
}

void loop() {
//controlleren of er een seriele verbinding is
  if (Serial.available() > 0) {
  //wanneer er verbinding is seriele verbinding regel uitlezen en toekennen aan variabele
  incomingByte = Serial.readStringUntil('\n');
    //wanneer emotie = ... functie uitvoeren(kleur licht(0x00,0x00,0x,00), snelheid effect)
    if (incomingByte == "happy") {
      
      RunningLights(0x00, 0xff, 0x00, 50);

    }

    else if (incomingByte == "sad") {

      RunningLights(0x00, 0x00, 0xff, 50);

    }

    else if (incomingByte == "fear") {

      RunningLights(0xff, 0xbb, 0x00, 50);

    }

    else if (incomingByte == "surprise") {

      RunningLights(0xff, 0xff, 0x00, 50);

    }

    else if (incomingByte == "angry") {

      RunningLights(0xff, 0x00, 0x00, 50);

    }

    else if (incomingByte == "disgust") {

      RunningLights(0xd8, 0x17, 0xff, 50);

    }

    else if (incomingByte == "neutral") {

      RunningLights(0xff, 0xff, 0xff, 50);

    }
    //wanneer geen gezicht gedetecteerd is standaard stukje verlichting draaien in ZUYD kleuren
    while (incomingByte == "NoFace") {

      CylonBounce(0xff, 0xff, 0xff, 40, 2, 10);
      colorWipe(0xff,0x00,0x00, 5);
      colorWipe(0xff,0xff,0xff, 5);
      colorWipe(0x00,0x00,0x00, 5);
      delay(5000);

    }

  }

}


//functies om verschillende animaties in verschillende kleuren uit te voeren
void colorWipe(byte red, byte green, byte blue, int SpeedDelay) {
  for(uint16_t i=0; i<NUM_LEDS; i++) {
      setPixel(i, red, green, blue);
      showStrip();
      delay(SpeedDelay);
  }
}

void RunningLights(byte red, byte green, byte blue, int WaveDelay) {
  int Position=0;
 
  for(int j=0; j<NUM_LEDS*2; j++)
  {
      Position++; // = 0; //Position + Rate;
      for(int i=0; i<NUM_LEDS; i++) {
        // sine wave, 3 offset waves make a rainbow!
        //float level = sin(i+Position) * 127 + 128;
        //setPixel(i,level,0,0);
        //float level = sin(i+Position) * 127 + 128;
        setPixel(i,((sin(i+Position) * 127 + 128)/255)*red,
                   ((sin(i+Position) * 127 + 128)/255)*green,
                   ((sin(i+Position) * 127 + 128)/255)*blue);
      }
     
      showStrip();
      delay(WaveDelay);
  }
}

void CylonBounce(byte red, byte green, byte blue, int EyeSize, int SpeedDelay, int ReturnDelay){

  for(int i = 0; i < NUM_LEDS-EyeSize-2; i++) {
    setAll(0,0,0);
    setPixel(i, red/10, green/10, blue/10);
    for(int j = 1; j <= EyeSize; j++) {
      setPixel(i+j, red, green, blue);
    }
    setPixel(i+EyeSize+1, red/10, green/10, blue/10);
    showStrip();
    delay(SpeedDelay);
  }

  delay(ReturnDelay);

  for(int i = NUM_LEDS-EyeSize-2; i > 0; i--) {
    setAll(0,0,0);
    setPixel(i, red/10, green/10, blue/10);
    for(int j = 1; j <= EyeSize; j++) {
      setPixel(i+j, red, green, blue);
    }
    setPixel(i+EyeSize+1, red/10, green/10, blue/10);
    showStrip();
    delay(SpeedDelay);
  }
 
  delay(ReturnDelay);
}


//standaard functies om led strip te definieren
void showStrip() {
 #ifdef ADAFRUIT_NEOPIXEL_H
   // NeoPixel
   strip.show();
 #endif
}

void setPixel(int Pixel, byte red, byte green, byte blue) {
 #ifdef ADAFRUIT_NEOPIXEL_H
   // NeoPixel
   strip.setPixelColor(Pixel, strip.Color(red, green, blue));
 #endif
 
}

void setAll(byte red, byte green, byte blue) {
  for(int i = 0; i < NUM_LEDS; i++ ) {
    setPixel(i, red, green, blue);
  }
  showStrip();
}
