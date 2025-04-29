freeze('internal_filesystem/', 'boot.py') # Hardware initialization
freeze('internal_filesystem/', 'main.py') # User Interface initialization
#freeze('', 'boot.py') # Hardware initialization
#freeze('', 'main.py') # User Interface initialization
freeze('internal_filesystem/lib', '') # Additional libraries
freeze('/home/user/sources/freezeFS/', 'freezefs_mount.py') # Built-in apps
