import lvgl as lv

import uio
import ujson
import uos

import _thread
import traceback

import mpos.info
import mpos.ui

# Run the script in the current thread:
def execute_script(script_source, is_file, is_launcher, is_graphical):
    thread_id = _thread.get_ident()
    compile_name = 'script' if not is_file else script_source
    print(f"Thread {thread_id}: executing script")
    try:
        if is_file:
            print(f"Thread {thread_id}: reading script from file {script_source}")
            with open(script_source, 'r') as f: # TODO: check if file exists first?
                script_source = f.read()
        if not is_graphical:
            script_globals = {
                '__name__': "__main__"
            }
        else: # is_graphical
            if is_launcher:
                prevscreen = None
                newscreen = mpos.ui.rootscreen
            else:
                prevscreen = lv.screen_active()
                newscreen=lv.obj()
                newscreen.set_size(lv.pct(100),lv.pct(100))
            lv.screen_load(newscreen)
            script_globals = {
                'lv': lv,
                'NOTIFICATION_BAR_HEIGHT': mpos.ui.NOTIFICATION_BAR_HEIGHT, # for apps that want to leave space for notification bar
                'appscreen': newscreen,
                'start_app': start_app, # for launcher apps
                'parse_manifest': parse_manifest, # for launcher apps
                'restart_launcher': restart_launcher, # for appstore apps
                'show_launcher': mpos.ui.show_launcher, # for apps that want to show the launcher
                'CURRENT_OS_VERSION': mpos.info.CURRENT_OS_VERSION, # for osupdate
                '__name__': "__main__"
            }
        print(f"Thread {thread_id}: starting script")
        try:
            compiled_script = compile(script_source, compile_name, 'exec')
            exec(compiled_script, script_globals)
        except Exception as e:
            print(f"Thread {thread_id}: exception during execution:")
            # Print stack trace with exception type, value, and traceback
            tb = getattr(e, '__traceback__', None)
            traceback.print_exception(type(e), e, tb)
        print(f"Thread {thread_id}: script {compile_name} finished")
        # Note that newscreen isn't deleted, as it might still be foreground, or it might be mpos.ui.rootscreen
    except Exception as e:
        print(f"Thread {thread_id}: error:")
        tb = getattr(e, '__traceback__', None)
        traceback.print_exception(type(e), e, tb)

# Run the script in a new thread:
def execute_script_new_thread(scriptname, is_file, is_launcher, is_graphical):
    print(f"main.py: execute_script_new_thread({scriptname},{is_file},{is_launcher})")
    try:
        # 168KB maximum at startup but 136KB after loading display, drivers, LVGL gui etc so let's go for 128KB for now, still a lot...
        # But then no additional threads can be created. A stacksize of 32KB allows for 4 threads, so 3 in the app itself, which might be tight.
        # 16KB allows for 10 threads in the apps, but seems too tight for urequests on unix (desktop) targets
        # 32KB seems better for the camera, but it forced me to lower other app threads from 16 to 12KB
        #_thread.stack_size(24576) # causes camera issue...
        #_thread.stack_size(16384)
        _thread.stack_size(32*1024)
        _thread.start_new_thread(execute_script, (scriptname, is_file, is_launcher, is_graphical))
    except Exception as e:
        print("main.py: execute_script_new_thread(): error starting new thread thread: ", e)

def start_app_by_name(app_name, is_launcher=False):
    mpos.ui.set_foreground_app(app_name)
    custom_app_dir=f"apps/{app_name}"
    builtin_app_dir=f"builtin/apps/{app_name}"
    try:
        stat = uos.stat(custom_app_dir)
        start_app(custom_app_dir, is_launcher)
    except OSError:
        start_app(builtin_app_dir, is_launcher)

def start_app(app_dir, is_launcher=False):
    print(f"main.py start_app({app_dir},{is_launcher}")
    mpos.ui.set_foreground_app(app_dir) # would be better to store only the app name...
    manifest_path = f"{app_dir}/META-INF/MANIFEST.JSON"
    app = parse_manifest(manifest_path)
    start_script_fullpath = f"{app_dir}/{app.entrypoint}"
    execute_script_new_thread(start_script_fullpath, True, is_launcher, True)
    # Launchers have the bar, other apps don't have it
    if is_launcher:
        mpos.ui.open_bar()
    else:
        mpos.ui.close_bar()


def restart_launcher():
    # No need to stop the other launcher first, because it exits after building the screen
    start_app_by_name("com.example.launcher", True)


def is_launcher(app_name):
    print(f"checking is_launcher for {app_name}")
    # Simple check, could be more elaborate by checking the MANIFEST.JSON for the app...
    return "launcher" in app_name


class App:
    def __init__(self, name, publisher, short_description, long_description, icon_url, download_url, fullname, version, entrypoint, category):
        self.name = name
        self.publisher = publisher
        self.short_description = short_description
        self.long_description = long_description
        self.icon_url = icon_url
        self.download_url = download_url
        self.fullname = fullname
        self.version = version
        self.entrypoint = entrypoint
        self.category = category
        self.image = None
        self.image_dsc = None

def parse_manifest(manifest_path):
    # Default values for App object
    default_app = App(
        name="Unknown",
        publisher="Unknown",
        short_description="",
        long_description="",
        icon_url="",
        download_url="",
        fullname="Unknown",
        version="0.0.0",
        entrypoint="assets/start.py",
        category=""
    )
    try:
        with open(manifest_path, 'r') as f:
            app_info = ujson.load(f)
            # Create App object with values from manifest, falling back to defaults
            return App(
                name=app_info.get("name", default_app.name),
                publisher=app_info.get("publisher", default_app.publisher),
                short_description=app_info.get("short_description", default_app.short_description),
                long_description=app_info.get("long_description", default_app.long_description),
                icon_url=app_info.get("icon_url", default_app.icon_url),
                download_url=app_info.get("download_url", default_app.download_url),
                fullname=app_info.get("fullname", default_app.fullname),
                version=app_info.get("version", default_app.version),
                entrypoint=app_info.get("entrypoint", default_app.entrypoint),
                category=app_info.get("category", default_app.category)
            )
    except OSError:
        print(f"parse_manifest: error loading manifest_path: {manifest_path}")
        return default_app

def auto_connect():
    # A generic "start at boot" mechanism hasn't been implemented yet, so do it like this:
    custom_auto_connect = "apps/com.example.wificonf/assets/auto_connect.py"
    builtin_auto_connect = "builtin/apps/com.example.wificonf/assets/auto_connect.py"
    # Maybe start_app_by_name() and start_app_by_name() could be merged so the try-except logic is not duplicated...
    try:
        stat = uos.stat(custom_auto_connect)
        execute_script_new_thread(custom_auto_connect, True, False, False)
    except OSError:
        try:
            print(f"Couldn't execute {custom_auto_connect}, trying {builtin_auto_connect}...")
            stat = uos.stat(builtin_auto_connect)
            execute_script_new_thread(builtin_auto_connect, True, False, False)
        except OSError:
            print("Couldn't execute {builtin_auto_connect}, continuing...")
    
