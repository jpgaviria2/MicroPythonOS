import ujson
import os

class SharedPreferences:
    def __init__(self, appname, filename="config.json"):
        """Initialize with appname and filename for preferences."""
        self.appname = appname
        self.filename = filename
        self.filepath = f"data/{self.appname}/{self.filename}"
        self.data = {}
        self.load()  # Load existing preferences

    def make_folder_structure(self):
        """Create directory structure if it doesn't exist."""
        #print("Checking if data/ exists")
        try:
            os.stat('data')
            #print("data/ exists")
        except OSError:
            print("Creating data/ directory")
            os.mkdir('data')
        #print(f"Checking if data/{self.appname}/ exists")
        try:
            os.stat(f"data/{self.appname}")
            #print(f"data/{self.appname}/ exists")
        except OSError:
            #print(f"Creating data/{self.appname} directory")
            os.mkdir(f"data/{self.appname}")

    def load(self):
        """Load preferences from the JSON file."""
        try:
            with open(self.filepath, 'r') as f:
                self.data = ujson.load(f)
                print(f"load: Loaded preferences: {self.data}")
        except Exception as e:
            print(f"load: Got exception {e}, assuming empty or non-existent preferences.")
            self.data = {}  # Default to empty dict on error

    def get_string(self, key, default=None):
        """Retrieve a string value for the given key, with a default if not found."""
        return str(self.data.get(key, default))

    def get_int(self, key, default=0):
        """Retrieve an integer value for the given key, with a default if not found."""
        try:
            return int(self.data.get(key, default))
        except (TypeError, ValueError):
            return default

    def get_bool(self, key, default=False):
        """Retrieve a boolean value for the given key, with a default if not found."""
        try:
            return bool(self.data.get(key, default))
        except (TypeError, ValueError):
            return default

    def edit(self):
        """Return an Editor object to modify preferences."""
        return Editor(self)

    def save_config(self):
        """Save preferences to the JSON file."""
        self.make_folder_structure()  # Ensure directories exist
        print(f"save_config: Saving preferences to {self.filepath}")
        try:
            with open(self.filepath, 'w') as f:
                ujson.dump(self.data, f)
            print("save_config: Saved")
        except Exception as e:
            print(f"save_config: Got exception {e}")

class Editor:
    def __init__(self, preferences):
        """Initialize Editor with a reference to SharedPreferences."""
        self.preferences = preferences
        self.temp_data = preferences.data.copy()  # Work on a copy of the data

    def put_string(self, key, value):
        """Store a string value."""
        self.temp_data[key] = str(value)
        return self

    def put_int(self, key, value):
        """Store an integer value."""
        self.temp_data[key] = int(value)
        return self

    def put_bool(self, key, value):
        """Store a boolean value."""
        self.temp_data[key] = bool(value)
        return self

    def apply(self):
        """Save changes to the file asynchronously (emulated)."""
        self.preferences.data = self.temp_data.copy()
        self.preferences.save_config()

    def commit(self):
        """Save changes to the file synchronously."""
        self.preferences.data = self.temp_data.copy()
        self.preferences.save_config()
        return True

# Example usage
def main():
    # Initialize SharedPreferences with an appname
    prefs = SharedPreferences("com.example.test_shared_prefs")
    
    print("Getting preferences:")
    print(f"theme: {prefs.get_string('theme')}")
    print(f"volume: {prefs.get_int('volume')}")
    print(f"notifications: {prefs.get_bool('notifications')}")
    print("Done getting preferences.")

    # Save some settings using Editor
    editor = prefs.edit()
    editor.put_string("theme", "dark")
    editor.put_int("volume", 75)
    editor.put_bool("notifications", True)
    editor.apply()  # Asynchronous save (emulated)

    # Read back the settings
    print("Theme:", prefs.get_string("theme", "light"))
    print("Volume:", prefs.get_int("volume", 50))
    print("Notifications:", prefs.get_bool("notifications", False))

    # Modify a setting
    editor = prefs.edit()
    editor.put_string("theme", "light")
    success = editor.commit()  # Synchronous save
    print("Save successful:", success)

    # Read updated setting
    print("Updated Theme:", prefs.get_string("theme", "light"))

if __name__ == '__main__':
    main()
