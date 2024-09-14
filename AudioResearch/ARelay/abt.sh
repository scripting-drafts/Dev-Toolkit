#! /bin/sh
echo 'Making arelay discoverable'
# sudo hciconfig hci0 up
# sudo hciconfig hci0 piscan
# sudo hciconfig hci0 sspmode 1
sudo bluetoothctl power on
sudo bluetoothctl discoverable on
sudo bluetoothctl pairable on
