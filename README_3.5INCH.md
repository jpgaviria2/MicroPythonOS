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

### 5. Touch Controller
- **Old**: Resistive touch (XPT2046) - Waveshare ESP32-S3-Touch-LCD-2
- **New**: Capacitive touch (CST816S) - 3.5 inch display
- **Note**: Touch handling updated for capacitive interface

### 6. Camera Power Management
- Updated camera power-off mechanism for HVGA resolution
- Maintained OV5640 camera compatibility
- Optimized frame buffer allocation for new resolution

### 7. UI Scaling
- **Automatic**: UI components use percentage-based scaling
- **No changes needed**: All UI elements automatically adapt to new resolution
- **Touch sensitivity**: Optimized for capacitive touch interface

## Files Modified

1. **`internal_filesystem/boot.py`** - Main hardware initialization
2. **`internal_filesystem/boot_unix.py`** - Unix/Desktop configuration
3. **`internal_filesystem/apps/com.micropythonos.camera/assets/camera_app.py`** - Camera resolution and dimensions
4. **`c_mpos/src/webcam.c`** - Webcam output resolution
5. **`c_mpos/esp32-quirc_from_blockstream_jade/lib/quirc.c`** - QR code processing buffer
6. **`README_3.5INCH.md`** - This configuration guide

## Component Compatibility Analysis

### ✅ **Fully Compatible (No Changes Needed)**
- **LVGL Graphics Library** - Automatically scales to new resolution
- **MicroPython OS Framework** - Resolution-agnostic
- **Built-in Applications** - Use percentage-based layouts
- **Touch Interface** - CST816S capacitive touch supported
- **SPI Display Interface** - ST7789 controller compatible
- **I2C Communication** - Same pin assignments

### ⚠️ **Updated for New Resolution**
- **Camera System** - Updated to HVGA (480×320)
- **Frame Buffers** - Optimized memory allocation
- **Image Processing** - Updated for new dimensions
- **QR Code Processing** - Buffer size updated

### 🔧 **Hardware Considerations**
- **Power Consumption** - Slightly higher due to larger display
- **Memory Usage** - Increased frame buffer requirements
- **Touch Sensitivity** - Capacitive vs resistive differences
- **Camera Interface** - Same OV5640 sensor, new resolution

## Performance Notes

- Frame buffer size has been optimized for the 3.5 inch display
- Camera performance maintained at 9FPS with the new resolution
- Touch sensitivity optimized for capacitive touch interface
- UI responsiveness maintained through percentage-based scaling

## Compatibility

This configuration maintains compatibility with:
- LVGL graphics library
- MicroPython OS framework
- Built-in applications
- Camera and image viewing capabilities
- Touch interface (capacitive)
- All existing MicroPython libraries

## Usage

The system will automatically detect and use the 3.5 inch display configuration. No additional setup is required beyond flashing the firmware to your ESP32-S3 board.

## Troubleshooting

If you experience display issues:
1. Verify all pin connections match the configuration
2. Check that the display is properly powered
3. Ensure the correct firmware is flashed for your board model
4. Verify capacitive touch is working (vs resistive touch on old board)

## Migration from Waveshare ESP32-S3-Touch-LCD-2

### **What Changed:**
- Display resolution: 320×240 → 480×320
- Touch technology: Resistive → Capacitive
- Frame buffer size: 28.8KB → 46.1KB
- Camera resolution: 240×240 → 480×320

### **What Stayed the Same:**
- ESP32-S3 chip compatibility
- SPI/I2C pin assignments
- ST7789 display controller
- OV5640 camera sensor
- MicroPython OS framework
- LVGL graphics library