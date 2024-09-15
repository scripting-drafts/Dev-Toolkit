# Audio-Relay

### HFP client with ffmpeg tunneling

Precompiled build:  
[![Download arelay](https://a.fsdn.com/con/app/sf-download-button)](https://sourceforge.net/projects/arelay/files/latest/download)  
  
Requirements:
 - [Raspbian 10](https://downloads.raspberrypi.org/raspbian/images/raspbian-2020-02-14/2020-02-13-raspbian-buster.zip) (32bit Debian Buster)
 - Raspberry Pi 3b or Zero W
 - 4gb micro sd card

Start with:
```sh
sudo apt-get purge chromium
sudo apt-get autoremove
sudo apt-get autoclean
sudo apt-get install ofono
```


In `/etc/dbus-1/system.d/ofono.conf` modify:

    <policy context="default">
        <deny send_destination="org.ofono"/>
    </policy>

to:

    <policy context="default">
        <allow send_destination="org.ofono"/>
    </policy>


Then:
```sh
git clone -b stable-14.x https://gitlab.freedesktop.org/pulseaudio/pulseaudio.git
```


In `src/modules/bluetooth/backend-native.c` and `src/modules/bluetooth/backend-ofono.c` change:
    
    *imtu = 48;
    
to:
    
    *imtu = 60;


Run the following:
```sh
sudo apt-get build-dep pulseaudio
cd pulseaudio
./bootstrap.sh && make && sudo make install && ldconfig
```

Limit profiles to HFP only in `/usr/local/etc/pulse/default.pa` by adding:

    .ifexists module-bluetooth-discover.so
    load-module module-bluetooth-discover autodetect_mtu=yes headset=ofono
    .endif


For multi-user usage:
```sh
sudo apt-mark hold *
```

### Pending:
 - Create services to run on boot:
```sh
systemctl enable --now ofono
pulseaudio --start
```
 - Lower default output volume
 - Tunnel audio through ssh
 - "logo.nologo" to the line in /boot/cmdline.txt
