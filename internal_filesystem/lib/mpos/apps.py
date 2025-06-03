import lvgl as lv

import uio
import ujson
import uos

import _thread
import traceback

import mpos.apps
import mpos.info
import mpos.ui

def good_stack_size():
    stacksize = 24*1024
    import sys
    if sys.platform == "esp32":
        stacksize = 16*1024
    return stacksize

# Run the script in the current thread:
def execute_script(script_source, is_file, cwd=None):
    thread_id = _thread.get_ident()
    compile_name = 'script' if not is_file else script_source
    print(f"Thread {thread_id}: executing script with cwd: {cwd}")
    try:
        if is_file:
            print(f"Thread {thread_id}: reading script from file {script_source}")
            with open(script_source, 'r') as f: # TODO: check if file exists first?
                script_source = f.read()
        script_globals = {
            'lv': lv,
            '__name__': "__main__"
        }
        print(f"Thread {thread_id}: starting script")
        import sys
        path_before = sys.path
        if cwd:
            sys.path.append(cwd)
        try:
            compiled_script = compile(script_source, compile_name, 'exec')
            exec(compiled_script, script_globals)
            # Introspect globals
            classes = {k: v for k, v in script_globals.items() if isinstance(v, type)}
            functions = {k: v for k, v in script_globals.items() if callable(v) and not isinstance(v, type)}
            variables = {k: v for k, v in script_globals.items() if not callable(v)}
            print("Classes:", classes.keys())
            print("Functions:", functions.keys())
            print("Variables:", variables.keys())
            MainActivity = script_globals.get("MainActivity")
            if MainActivity:
                loaded_activity = MainActivity()
                loaded_activity.onCreate()  # Call lifecycle method
        except Exception as e:
            print(f"Thread {thread_id}: exception during execution:")
            # Print stack trace with exception type, value, and traceback
            tb = getattr(e, '__traceback__', None)
            traceback.print_exception(type(e), e, tb)
        print(f"Thread {thread_id}: script {compile_name} finished")
        sys.path = path_before
    except Exception as e:
        print(f"Thread {thread_id}: error:")
        tb = getattr(e, '__traceback__', None)
        traceback.print_exception(type(e), e, tb)

# Run the script in a new thread:
# TODO: check if the script exists here instead of launching a new thread?
def execute_script_new_thread(scriptname, is_file):
    print(f"main.py: execute_script_new_thread({scriptname},{is_file})")
    try:
        # 168KB maximum at startup but 136KB after loading display, drivers, LVGL gui etc so let's go for 128KB for now, still a lot...
        # But then no additional threads can be created. A stacksize of 32KB allows for 4 threads, so 3 in the app itself, which might be tight.
        # 16KB allows for 10 threads in the apps, but seems too tight for urequests on unix (desktop) targets
        # 32KB seems better for the camera, but it forced me to lower other app threads from 16 to 12KB
        #_thread.stack_size(24576) # causes camera issue...
        # NOTE: This doesn't do anything if apps are started in the same thread!
        if "camtest" in scriptname:
            print("Starting camtest with extra stack size!")
            stack=32*1024
        elif "appstore"in scriptname:
            print("Starting appstore with extra stack size!")
            stack=24*1024 # this doesn't do anything because it's all started in the same thread
        else:
            stack=16*1024 # 16KB doesn't seem to be enough for the AppStore app on desktop
        stack = mpos.apps.good_stack_size()
        print(f"app.py: setting stack size for script to {stack}")
        _thread.stack_size(stack)
        _thread.start_new_thread(execute_script, (scriptname, is_file))
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
    print(f"main.py start_app({app_dir},{is_launcher})")
    mpos.ui.set_foreground_app(app_dir) # would be better to store only the app name...
    manifest_path = f"{app_dir}/META-INF/MANIFEST.JSON"
    app = mpos.apps.parse_manifest(manifest_path)
    start_script_fullpath = f"{app_dir}/{app.entrypoint}"
    #execute_script_new_thread(start_script_fullpath, True, is_launcher, True) # Starting (GUI?) apps in a new thread can cause hangs (GIL lock?)
    execute_script(start_script_fullpath, True, app_dir + "/assets/")
    # Launchers have the bar, other apps don't have it
    if is_launcher:
        mpos.ui.open_bar()
    else:
        mpos.ui.close_bar()

def restart_launcher():
    mpos.ui.empty_screen_stack()
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
        execute_script_new_thread(custom_auto_connect, True)
    except Exception as e:
        try:
            print(f"Couldn't execute {custom_auto_connect} because exception {e}, trying {builtin_auto_connect}...")
            stat = uos.stat(builtin_auto_connect)
            execute_script_new_thread(builtin_auto_connect, True)
        except Exception as e:
            print("Couldn't execute {builtin_auto_connect} because exception {e}, continuing...")
    

class Activity:

    def onCreate(self):
        pass
    def onStart(self, screen):
        pass
    def onResume(self, screen):
        pass
    def onPause(self, screen):
        pass
    def onStop(self, screen):
        pass
    def onDestroy(self, screen):
        pass
