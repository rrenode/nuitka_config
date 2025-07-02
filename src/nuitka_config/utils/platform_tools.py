import platform

def get_os():
    system = platform.system().lower()

    if "windows" in system:
        return "windows"
    elif "darwin" in system:
        return "mac"
    elif "linux" in system:
        return "linux"
    else:
        return "unknown"

def pick_for_platform(windows_option=None, mac_option=None, linux_option=None, default=None):
    _os = get_os()

    match _os:
        case "windows":
            if windows_option is not None:
                return windows_option
        case "mac":
            if mac_option is not None:
                return mac_option
        case "linux":
            if linux_option is not None:
                return linux_option

    return default  # Fallback if none matched or option was None
