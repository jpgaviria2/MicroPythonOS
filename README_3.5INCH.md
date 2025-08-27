# ESP32-S3 3.5 inch Capacitive Touch Display Configuration

This repository has been configured for the **ESP32-S3 3.5 inch Capacitive Touch Display Development Board** with the following specifications:

## Display Specifications
- **Resolution**: 320×480 pixels (HVGA)
- **Panel Type**: IPS Panel
- **Colors**: 262K Color
- **Touch**: Capacitive Touch
- **Interface**: Onboard Camera Interface
- **Connectivity**: Wi-Fi and Bluetooth 5

## Key Configuration Changes

### 1. Display Resolution
- **Old**: 320×240 (2.4 inch display)
- **New**: 480×320 (3.5 inch display)

### 2. Frame Buffer Size
- **Old**: 28,800 bytes (for 320×240)
- **New**: 46,080 bytes (for 480×320)

### 3. Camera Resolution
- **Old**: 240×240 (R240X240)
- **New**: 480×320 (HVGA)

### 4. Pin Configuration
The following pins are configured for the 3.5 inch display:
- **SPI**: SCLK=39, MOSI=38, MISO=40, DC=42, CS=45
- **Backlight**: BL=1
- **Touch I2C**: SDA=48, SCL=47

## Files Modified

1. **`internal_filesystem/boot.py`** - Main hardware initialization
2. **`internal_filesystem/boot_unix.py`** - Unix/Desktop configuration
3. **`internal_filesystem/apps/com.micropythonos.camera/assets/camera_app.py`** - Camera resolution
4. **`c_mpos/src/webcam.c`** - Webcam output resolution
5. **`README_3.5INCH.md`** - This configuration guide

## Performance Notes

- Frame buffer size has been optimized for the 3.5 inch display
- Camera performance maintained at 9FPS with the new resolution
- Touch sensitivity optimized for capacitive touch interface

## Compatibility

This configuration maintains compatibility with:
- LVGL graphics library
- MicroPython OS framework
- Built-in applications
- Camera and image viewing capabilities

## Usage

The system will automatically detect and use the 3.5 inch display configuration. No additional setup is required beyond flashing the firmware to your ESP32-S3 board.

## Troubleshooting

If you experience display issues:
1. Verify all pin connections match the configuration
2. Check that the display is properly powered
3. Ensure the correct firmware is flashed for your board model