# Copyright (c) 2024 - 2025 Kevin G. Schlosser

################################################################################
# lcd_bus build rules

MOD_DIR := $(USERMOD_DIR)

ifneq (,$(findstring -Wno-missing-field-initializers, $(CFLAGS_USERMOD)))
    CFLAGS_USERMOD += -Wno-missing-field-initializers
endif

SRC_USERMOD_C += $(MOD_DIR)/src/hello_world.c
SRC_USERMOD_C += $(MOD_DIR)/src/quirc_decode.c
SRC_USERMOD_C += $(MOD_DIR)/src/webcam.c

SRC_USERMOD_C += $(MOD_DIR)/quirc/lib/identify.c
SRC_USERMOD_C += $(MOD_DIR)/quirc/lib/version_db.c
SRC_USERMOD_C += $(MOD_DIR)/quirc/lib/decode.c
SRC_USERMOD_C += $(MOD_DIR)/quirc/lib/quirc.c
#SRC_USERMOD_C += $(MOD_DIR)/quirc/openmv/collections.c

CFLAGS+= -I/usr/include
LDFLAGS+= -lv4l2
