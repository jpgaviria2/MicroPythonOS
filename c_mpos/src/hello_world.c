#include "py/obj.h"
#include "py/runtime.h"


//#error "building hello world from lcd_utils"

// C function to print "Hello World"
static mp_obj_t hello_world(void) {
    printf("Hello World from C compiled!\n");
    return mp_const_none; // MicroPython functions typically return None
}

// Define the function entry in the module
static MP_DEFINE_CONST_FUN_OBJ_0(hello_world_obj, hello_world);

// Module function table
static const mp_rom_map_elem_t hello_world_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_hello_world) },
    { MP_ROM_QSTR(MP_QSTR_hello), MP_ROM_PTR(&hello_world_obj) },
};

// Module globals dictionary
static MP_DEFINE_CONST_DICT(hello_world_module_globals, hello_world_module_globals_table);

// Module definition
const mp_obj_module_t hello_world_module = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&hello_world_module_globals,
};

// Register the module with MicroPython
MP_REGISTER_MODULE(MP_QSTR_hello_world, hello_world_module);
