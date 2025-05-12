# Copyright (c) 2024 - 2025 Kevin G. Schlosser

# Create an INTERFACE library for our C module.

add_library(usermod_c_mpos INTERFACE)

set(MPOS_C_INCLUDES)

set(MPOS_C_SOURCES
    ${CMAKE_CURRENT_LIST_DIR}/src/hello_world.c
)

# Add our source files to the lib
target_sources(usermod_c_mpos INTERFACE ${MPOS_C_SOURCES})

# Add include directories.
target_include_directories(usermod_c_mpos INTERFACE ${MPOS_C_INCLUDES})

# Link our INTERFACE library to the usermod target.
target_link_libraries(usermod INTERFACE usermod_c_mpos)
