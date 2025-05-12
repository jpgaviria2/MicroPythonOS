fwfile="/home/user/sources/lvgl_micropython/build/lvgl_micropy_ESP32_GENERIC_S3-SPIRAM_OCT-16.bin"
ls -al $fwfile
#~/.espressif/python_env/idf5.2_py3.9_env/bin/python -m esptool --chip esp32s3 --before default_reset --after hard_reset write_flash --flash_mode dio --flash_size 16MB --flash_freq 80m --erase-all  0x0 $fwfile
~/.espressif/python_env/idf5.2_py3.9_env/bin/python -m esptool --chip esp32s3 --before default_reset --after hard_reset write_flash --flash_mode dio --flash_size 16MB --flash_freq 80m 0x0 $fwfile

