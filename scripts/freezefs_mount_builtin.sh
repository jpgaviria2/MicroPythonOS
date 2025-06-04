pushd ~/sources/freezeFS
python3 -m freezefs --target /builtin --on-import mount ~/sources/MicroPythonOS/internal_filesystem/builtin freezefs_mount_builtin.py
popd
