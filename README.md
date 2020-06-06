# 2JCIE-BU to Machinist

![Docker Cloud Automated build](https://img.shields.io/docker/cloud/automated/vet5lqplpecmpnqb/2jciebu-machinist?label=DOCKER%20BUILD)
![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/vet5lqplpecmpnqb/2jciebu-machinist?label=DOCKER%20BUILD)


OMRON USB環境センサ [2JCIE-BU](https://www.omron.co.jp/ecb/product-detail?partId=73063)から取得した値を、IIJが提供するデータ分析基盤[Machinist](https://machinist.iij.jp/)に投入するスクリプトです。

![2jicebu](https://user-images.githubusercontent.com/5038337/78339365-513f3b80-75cf-11ea-8e90-483894f71502.png)

Dockerコンテナで動作します。

# 準備

## 用意するもの
- [OMRON 2JCIE-BU](https://www.omron.co.jp/ecb/product-detail?partId=73063)

![73063](https://user-images.githubusercontent.com/5038337/78334071-0d940400-75c6-11ea-9939-7b618b511d24.gif)

- Machinistアカウント

無料で取得できます。

https://app.machinist.iij.jp/sign-up

<img width="2032" alt="custom-charts" src="https://user-images.githubusercontent.com/5038337/78334190-4af89180-75c6-11ea-814c-9a6c8cdf1a1f.png">

- 常時稼働させられる端末

![raspi](https://user-images.githubusercontent.com/5038337/78334741-4680a880-75c7-11ea-874d-331919984a66.png)

![friendryelec](https://user-images.githubusercontent.com/5038337/78334816-6617d100-75c7-11ea-8137-955a85d6252c.png)

など

# 手順
## udevルール作成
/etc/udev/rules.d/10-2JCIE-BU.rules
```
ACTION=="add", \
ATTRS{idVendor}=="0590", \
ATTRS{idProduct}=="00d4", \
RUN+="/sbin/modprobe ftdi_sio" \
RUN+="/bin/sh -c 'echo 0590 00d4 > /sys/bus/usb-serial/drivers/ftdi_sio/new_id'", \
SYMLINK+="2JCIE-BU"
```
udevd restart
```
systemctl udevd restart
```

## 2JCIE-BU取付

## リポジトリクローン
```
git clone https://github.com/yasu-hide/2jciebu-machinist
```

## 設定編集
詳細は 設定ファイル (.envファイル) を参照
```
cd 2jciebu-machinist
cat <<'EOF' > .env
SENSOR_SERIAL_DEVICE=/dev/ttyUSB0
MACHINIST_APIKEY=(MACHINIST APIKEY)
MACHINIST_AGENT=(MACHINIST_AGENT)
MACHINIST_AGENT_ID=(MACHINIST_AGENT_ID)
MACHINIST_NAMESPACE=(MACHINIST NAMESPACE)
MACHINIST_TAGS=(MACHINIST_TAGS)
MACHINIST_SEND_METRICS=temperature relative_humidity ambient_light ...
EOF
```

## Dockerコンテナ起動
```
docker-compose up -d
```

## Enjoy!

# 設定ファイル (.envファイル)
## SENSOR_SERIAL_DEVICE
シリアルポートのデバイスファイルを指定

/dev/ttyUSB0以外を指定する場合、docker-compose.ymlの _devices_ も見直すこと

無指定の場合は __/dev/ttyUSB0__

## MACHINIST_APIKEY
Machinistにデータを投入するためのAPIキー

[Machinist アカウント設定](https://app.machinist.iij.jp/profile) から取得

無指定の場合は __空文字__

## MACHINIST_AGENT
Machinistに投入するデータのAgent

MACHINIST_AGENT または MACHINIST_AGENT_ID が必須

## MACHINIST_AGENT_ID
Machinistに投入するデータのAgent ID

MACHINIST_AGENT または MACHINIST_AGENT_ID が必須

## MACHINIST_NAMESPACE
Machinistに投入するデータの名前空間

## MACHINIST_TAGS
Machinistに投入するデータのタグ

スペース区切りで記述

キーと値をコロン(:)で分割して指定

## MACHINIST_SEND_METRICS
Machinistに投入するデータの種類

スペース区切りで記述

クオートの括り( "" や '' )は不要

指定できる値 (13種類)
```
temperature  気温
relative_humidity  相対湿度
ambient_light  照度
barometric_pressure  気圧
sound_noise  騒音
eTVOC  総揮発性有機化学物量相当値
eCO2  二酸化炭素濃度相当値
discomfort_index  不快指数
heat_stroke  熱中症警戒度
vibration_information  振動情報
si_value  スペクトル強度
pga  最大加速度値
seismic_intensity  震度
```

# 参考情報
- 形2JCIE-BU　環境センサ USB型 | OMRON - Japan - https://www.omron.co.jp/ecb/product-detail?partNumber=2JCIE-BU
- omron-devhub/2jciebu-usb-raspberrypi - https://github.com/omron-devhub/2jciebu-usb-raspberrypi
- OMRON USB型環境センサー 2JCIE-BUをLinux(debian9/OpenBlocks IoT)からUSB接続して使用する - Qiita - https://qiita.com/goto2048/items/d2706088af90503dd4c8
- OMRON USB型環境センサーをLinux(debian9)にUSB接続する | ぷらっとブログ - https://blog.plathome.co.jp/omron-usb-environment-sensor-2jcie-bu-debian-9-openblocks-iot/
