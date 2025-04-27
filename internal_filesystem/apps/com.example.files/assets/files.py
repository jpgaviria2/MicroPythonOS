import lvgl as lv
import uos
import vfs
import machine
import time

# LVGL File System Driver for LittleFS
class LittleFSDriver:
    def __init__(self, letter='L'):
        self.letter = letter
        self.files = {}
    def init(self):
        drv = lv.fs_drv_t()
        lv.fs_drv_init(drv)
        drv.letter = ord(self.letter)
        drv.open_cb = self.open_cb
        drv.close_cb = self.close_cb
        drv.read_cb = self.read_cb
        drv.write_cb = self.write_cb
        drv.seek_cb = self.seek_cb
        drv.tell_cb = self.tell_cb
        drv.dir_open_cb = self.dir_open_cb
        drv.dir_read_cb = self.dir_read_cb
        drv.dir_close_cb = self.dir_close_cb
        lv.fs_drv_register(drv)
    def open_cb(self, drv, path, mode):
        path = path.decode().lstrip(self.letter + ':')
        try:
            if mode & lv.FS_MODE_WR:
                file = open(path, 'wb' if mode == lv.FS_MODE_WR else 'r+b')
            else:
                file = open(path, 'rb')
            self.files[id(file)] = file
            return id(file)
        except Exception as e:
            print(f"Open error: {e}")
            return None
    def close_cb(self, drv, file_p):
        file_id = file_p
        if file_id in self.files:
            self.files[file_id].close()
            del self.files[file_id]
            return lv.FS_RES_OK
        return lv.FS_RES_NOT_EX
    def read_cb(self, drv, file_p, buf, btr, br):
        file_id = file_p
        if file_id in self.files:
            try:
                data = self.files[file_id].read(btr)
                br[0] = len(data)
                for i, b in enumerate(data):
                    buf[i] = b
                return lv.FS_RES_OK
            except:
                return lv.FS_RES_FS_ERR
        return lv.FS_RES_NOT_EX
    def write_cb(self, drv, file_p, buf, btw, bw):
        file_id = file_p
        if file_id in self.files:
            try:
                data = bytes([buf[i] for i in range(btw)])
                self.files[file_id].write(data)
                bw[0] = btw
                return lv.FS_RES_OK
            except:
                return lv.FS_RES_FS_ERR
        return lv.FS_RES_NOT_EX
    def seek_cb(self, drv, file_p, pos, whence):
        file_id = file_p
        if file_id in self.files:
            try:
                if whence == lv.FS_SEEK_SET:
                    self.files[file_id].seek(pos, 0)
                elif whence == lv.FS_SEEK_CUR:
                    self.files[file_id].seek(pos, 1)
                elif whence == lv.FS_SEEK_END:
                    self.files[file_id].seek(pos, 2)
                return lv.FS_RES_OK
            except:
                return lv.FS_RES_FS_ERR
        return lv.FS_RES_NOT_EX
    def tell_cb(self, drv, file_p, pos):
        file_id = file_p
        if file_id in self.files:
            try:
                pos[0] = self.files[file_id].tell()
                return lv.FS_RES_OK
            except:
                return lv.FS_RES_FS_ERR
        return lv.FS_RES_NOT_EX
    def dir_open_cb(self, drv, path):
        path = path.decode().lstrip(self.letter + ':')
        try:
            dir_list = uos.listdir(path or '/')
            dir_obj = {'path': path or '/', 'list': dir_list, 'index': 0}
            dir_id = id(dir_obj)
            self.files[dir_id] = dir_obj
            return dir_id
        except:
            return None
    def dir_read_cb(self, drv, dir_p, fn):
        dir_id = dir_p
        if dir_id in self.files:
            dir_obj = self.files[dir_id]
            if dir_obj['index'] < len(dir_obj['list']):
                name = dir_obj['list'][dir_obj['index']]
                try:
                    uos.stat(dir_obj['path'] + '/' + name + '/')
                    name = '/' + name
                except:
                    pass
                dir_obj['index'] += 1
                fn.assign(name)
                return lv.FS_RES_OK
            fn.assign('')
            return lv.FS_RES_OK
        return lv.FS_RES_NOT_EX
    def dir_close_cb(self, drv, dir_p):
        dir_id = dir_p
        if dir_id in self.files:
            del self.files[dir_id]
            return lv.FS_RES_OK
        return lv.FS_RES_NOT_EX


# Register the LittleFS driver
fs_drv = LittleFSDriver('L')
fs_drv.init()

# Create subwindow
subwindow = lv.obj()
subwindow.set_size(lv.pct(100), lv.pct(100))
# Create File Explorer
def file_explorer_event_cb(e):
    code = e.get_code()
    obj = e.get_target()
    if code == lv.EVENT.VALUE_CHANGED:
        file_path = obj.get_selected_file_path()
        print(f"Selected file: {file_path}")


subwindow.clean()
explorer = lv.file_explorer(subwindow)
explorer.set_size(lv.pct(100), lv.pct(100))
explorer.explorer_set_quick_access_path(lv.EXPLORER.HOME_DIR,"/")
explorer.explorer_open_dir("/apps")
#explorer.set_root_path("L:/")
explorer.add_event_cb(file_explorer_event_cb, lv.EVENT.VALUE_CHANGED, None)
