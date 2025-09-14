# Pico MIDI Controller

Raspberry Pi Pico (RP2040) + CircuitPython を使った **USB-MIDIコントローラ** のサンプルです。
タクトスイッチで **Note On/Off**、ポテンショメータで **MIDI CC** を送信します。

---

## Features

* 1ボタンで **Note On / Note Off (C4)** を送信
* 1ポテンショメータで **Control Change (CC1: Modulation Wheel)** を送信
* デバウンス / ADCオーバーサンプリング / ヒステリシス処理 / デッドゾーン処理を実装し、安定した操作感
* オンボードLEDで Note On 状態を表示

---

## Requirements

* Raspberry Pi Pico または Pico W
* CircuitPython (例: 9.x)
* [Adafruit CircuitPython Library Bundle](https://circuitpython.org/libraries) から
  `adafruit_midi` を `CIRCUITPY/lib/` にコピー
* タクトスイッチ ×1
* ポテンショメータ (10kΩ 推奨) ×1

---

## Wiring

### Button

* GP15 ↔ ボタン ↔ GND

### Potentiometer

* 片端 → 3V3(OUT)
* 片端 → GND
* 中央端子 → GP26 (ADC0)

> ⚠️ 注意: 必ず **3V3(OUT)** を使用してください。VBUS (5V) では壊れる可能性があります。

---

## Usage

1. `code.py` を `CIRCUITPY` ドライブ直下にコピー
2. PCにUSB接続すると「CircuitPython MIDI」として認識
3. DAWやMIDIモニタで入力デバイスを設定
4. ボタンを押す → Note On
   ボタンを離す → Note Off
   ツマミを回す → CC#1 (0–127)

---

## Example Code

（リポジトリには `code.py` として含まれています）

```python
import time, board, digitalio, analogio, usb_midi
from adafruit_midi import MIDI
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff
from adafruit_midi.control_change import ControlChange

# …中略（詳細コードは code.py を参照）…
```

---

## Notes

* `usb_midi.ports[1]` が環境によっては `ports[0]` になる場合があります
* 複数のボタンやツマミを追加する場合は、GP27/GP28などADCピンを利用可能
* CC番号を変更することで、ボリューム (CC7) やパン (CC10) などに割り当てもできます

---

## Next Steps

* ボタンやツマミを増やしてミニMIDIコントローラ化
* エンコーダやタッチセンサーを追加
* ケースや基板化で実用ハードに発展
