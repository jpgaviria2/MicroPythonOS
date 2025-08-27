# Firmware Build Guide for ESP32-S3 3.5 inch Display

This guide covers building the firmware for the ESP32-S3 3.5 inch Capacitive Touch Display Development Board.

## Build Requirements

### Prerequisites
- MicroPython LVGL build environment
- ESP-IDF toolchain
- Python 3.x
- Required dependencies (see main README)

### Build Configuration

The firmware is configured for:
- **Board**: ESP32_GENERIC_S3
- **Variant**: SPIRAM_OCT (8MB PSRAM)
- **Display**: ST7789 (3.5 inch 320×480)
- **Touch**: CST816S (Capacitive)
- **Camera**: OV5640 (HVGA 480×320)

## Build Commands

### Production Build (Recommended)
```bash
./scripts/build_lvgl_micropython.sh esp32 prod
```

### Development Build
```bash
./scripts/build_lvgl_micropython.sh esp32 dev
```

## Build Flags

The build script automatically includes these flags:
- `--ota`: Over-the-air update support
- `--partition-size=4194304`: 4MB OTA partitions
- `--flash-size=16`: 16MB total flash
- `BOARD=ESP32_GENERIC_S3`: ESP32-S3 generic board
- `BOARD_VARIANT=SPIRAM_OCT`: 8MB PSRAM configuration
- `DISPLAY=st7789`: ST7789 display driver
- `INDEV=cst816s`: CST816S capacitive touch driver

## Memory Configuration

### Frame Buffer Optimization
- **Display Resolution**: 480×320 pixels
- **Color Depth**: RGB565 (2 bytes per pixel)
- **Total Pixels**: 153,600
- **Frame Buffer Size**: 46,080 bytes (optimized)
- **Memory Type**: Internal + DMA

### PSRAM Usage
- **Available PSRAM**: 8MB
- **Frame Buffers**: 2×46KB (92KB total)
- **Camera Buffers**: Optimized for HVGA
- **Remaining PSRAM**: ~7.9MB for applications

## Build Output

After successful build:
1. **Firmware**: `lvgl_micropython/build-esp32/firmware.bin`
2. **Partition Table**: `lvgl_micropython/build-esp32/partition-table.bin`
3. **Bootloader**: `lvgl_micropython/build-esp32/bootloader.bin`

## Flashing

### USB Flashing
```bash
./scripts/flash_over_usb.sh
```

### Manual Flashing
```bash
esptool.py --chip esp32s3 --port /dev/ttyUSB0 \
  --baud 921600 \
  --before default_reset \
  --after hard_reset \
  write_flash \
  --flash_mode dio \
  --flash_freq 80m \
  --flash_size 16MB \
  0x0 bootloader.bin \
  0x8000 partition-table.bin \
  0x10000 firmware.bin
```

## Post-Build Setup

### First Boot
1. Flash the firmware
2. Power on the device
3. The system will automatically detect the 3.5 inch display
4. Touch calibration may be required on first boot

### Verification
- Display should show 480×320 resolution
- Capacitive touch should be responsive
- Camera should work at HVGA resolution
- All UI elements should be properly scaled

## Troubleshooting

### Build Issues
- Ensure ESP-IDF is properly installed
- Check Python dependencies
- Verify board configuration

### Runtime Issues
- **Display Issues**: Check SPI pin connections
- **Touch Issues**: Verify I2C touch controller
- **Camera Issues**: Check camera power management
- **Memory Issues**: Verify PSRAM configuration

## Performance Notes

- **Frame Rate**: Optimized for smooth UI
- **Touch Response**: Capacitive touch optimized
- **Camera Performance**: 9FPS at HVGA resolution
- **Memory Usage**: Efficient frame buffer management

## Compatibility

This build is compatible with:
- ESP32-S3 boards with 8MB+ PSRAM
- ST7789 display controllers
- CST816S capacitive touch controllers
- OV5640 camera sensors
- MicroPython LVGL framework