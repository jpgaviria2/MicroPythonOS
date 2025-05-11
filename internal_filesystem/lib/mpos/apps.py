
def is_launcher(app_name):
    print(f"checking is_launcher for {app_name}")
    # Simple check, could be more elaborate by checking the MANIFEST.JSON for the app...
    return "launcher" in app_name
