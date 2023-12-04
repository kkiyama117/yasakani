# kizaru

京都大学11月祭で公開した「京大黄猿同好会」の企画の内部実装です. 
発案は音割れポッター同好会長発案、仕様は会長のイメージを落とし込みました


ラズパイの4B及び
  - タクトスイッチの類 -> スタート用
  - (リレースイッチ+USB-GPIO変換ケーブル)x2 -> USB制御電源タップ
  - LED(本番は白を利用、色は任意だが抵抗に注意) -> LED
を利用しています.

## Prerequirements

- pigpio library (for pigpio python library)
- ALSA(aplay)

