pushd ~/projects/MicroPythonOS/freezeFS
python3 -m freezefs --target /builtin --on-import mount ~/projects/MicroPythonOS/MicroPythonOS/internal_filesystem/builtin freezefs_mount_builtin.py
popd
