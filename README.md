[![Build Status](https://travis-ci.org/macrat/projectR-teamC.svg?branch=master)](https://travis-ci.org/macrat/projectR-teamC)

Overview
========
プロジェクト実習テーマR チームCの制御プログラム

Dependencies
============

## 機体

|型番等                     |用途              |数量|
|---------------------------|------------------|----|
|FRDM-KL25Z                 |機体の制御        | 1台|
|bluetoothシリアルモジュール|通信              | 1つ|
|DCモーター                 |車体とアームの移動| 4つ|
|Toshiba TB6612FNG          |DCモータの制御    | 2つ|
|Futaba RS304MD             |ハンドの開閉      | 1つ|

## コントローラ

- bluetoothの使えるPC

	unix系が良いかも？

	- Python3.x
	- PySerial
	- pygame

- ゲームコントローラ

	無くてもKeyboardControllerを使うなら問題無い。
