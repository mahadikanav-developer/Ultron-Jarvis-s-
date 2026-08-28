import os
import platform
import subprocess
from datetime import datetime


class Tools:
    """
    ULTRON SYSTEM TOOLS

    OS-agnostic command execution. Adapts to Windows, macOS, and Linux automatically.
    """

    def __init__(self):
        # Detect the operating system once upon initialization
        self.os_name = platform.system().lower()

    def execute_command(self, command):

        if not command:
            return {"success": False, "message": "No command provided."}

        # ------------------------------------------------------------
        # DYNAMIC APP LAUNCHING
        # ------------------------------------------------------------
        if command.startswith("open:"):
            app_name = command.split(":", 1)[1].strip()
            return self.open_app(app_name)

        # ------------------------------------------------------------
        # SCREENSHOT
        # ------------------------------------------------------------
        if command == "screenshot":
            return self.take_screenshot()

        # ------------------------------------------------------------
        # SYSTEM LOCK
        # ------------------------------------------------------------
        if command == "lock_system":
            return self.lock_system()

        # ------------------------------------------------------------
        # SYSTEM SHUTDOWN
        # ------------------------------------------------------------
        if command == "shutdown_system":
            return self.shutdown_system()

        return {
            "success": False,
            "message": f"I don't know how to execute the command: {command}"
        }

# ================================================================
    # OS-AGNOSTIC APP LAUNCHER
    # ================================================================
    def open_app(self, app_name):
        """
        Opens an application using native OS routing. 
        Includes fuzzy Start Menu searching for Windows.
        """
        try:
            if self.os_name == "windows":

                # 1. Map known modern Windows apps to their URIs
                special_apps = {
                    "settings": "ms-settings:",
                    "calculator": "calc",
                    "store": "ms-windows-store:",
                    "mail": "outlookmail:",
                    "photos": "ms-photos:",
                    "edge": "microsoft-edge:"
                }

                target = special_apps.get(app_name, app_name)

                # 2. Try native Python startfile (silent fail if not found)
                try:
                    os.startfile(target)
                    return {"success": True, "message": f"Opening {app_name.title()}."}
                except (FileNotFoundError, OSError):
                    pass  # Fails silently and moves to the fuzzy search

                # 3. If standard launch fails, use PowerShell to search the Start Menu
                ps_script = f"""
                $app = Get-StartApps | Where-Object {{ $_.Name -imatch '{app_name}' }} | Select-Object -First 1
                if ($app) {{
                    explorer.exe shell:appsFolder\\$($app.AppID)
                    exit 0
                }} else {{
                    exit 1
                }}
                """

                ps_result = subprocess.run(
                    ["powershell", "-command", ps_script],
                    capture_output=True
                )

                if ps_result.returncode == 0:
                    return {"success": True, "message": f"Opening {app_name.title()}."}

                return {
                    "success": False,
                    "message": f"I couldn't find an app named '{app_name}' on your system."
                }

            elif self.os_name == "darwin":  # macOS
                result = subprocess.run(
                    ["open", "-a", app_name], capture_output=True)
                if result.returncode == 0:
                    return {"success": True, "message": f"Opening {app_name.title()}."}
                return {"success": False, "message": f"Could not find '{app_name}' on macOS."}

            elif self.os_name == "linux":
                subprocess.Popen(
                    [app_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return {"success": True, "message": f"Opening {app_name.title()}."}

        except Exception as error:
            return {
                "success": False,
                "message": f"Error opening {app_name}: {error}"
            }

    # ================================================================
    # SCREENSHOT CAPTURE
    # ================================================================
    def take_screenshot(self):
        """
        Captures a screenshot using OS-native tools or Python libraries.
        Saves it to the desktop.
        """
        try:
            # Determine desktop path
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = os.path.join(
                desktop, f"ULTRON_Screenshot_{timestamp}.png")

            if self.os_name == "windows":
                # Uses PowerShell to take a screenshot natively in Windows 10/11
                ps_script = (
                    "Add-Type -AssemblyName System.Windows.Forms; "
                    "Add-Type -AssemblyName System.Drawing; "
                    "$Screen = [System.Windows.Forms.SystemInformation]::VirtualScreen; "
                    f"$Bitmap = New-Object System.Drawing.Bitmap $Screen.Width, $Screen.Height; "
                    "$Graphics = [System.Drawing.Graphics]::FromImage($Bitmap); "
                    "$Graphics.CopyFromScreen($Screen.Left, $Screen.Top, 0, 0, $Bitmap.Size); "
                    f"$Bitmap.Save('{filename}');"
                )
                subprocess.run(["powershell", "-command",
                               ps_script], capture_output=True)

            elif self.os_name == "darwin":
                # macOS native screenshot command
                subprocess.run(["screencapture", filename])

            elif self.os_name == "linux":
                # Linux usually has scrot or gnome-screenshot
                subprocess.run(["scrot", filename])

            return {
                "success": True,
                "message": f"Screenshot saved to your Desktop."
            }

        except Exception as error:
            return {
                "success": False,
                "message": f"Failed to take a screenshot: {error}"
            }

    # ================================================================
    # SYSTEM LOCK
    # ================================================================
    def lock_system(self):
        try:
            if self.os_name == "windows":
                os.system("rundll32.exe user32.dll,LockWorkStation")
            elif self.os_name == "darwin":
                os.system("pmset displaysleepnow")

            return {"success": True, "message": "System locked."}
        except Exception:
            return {"success": False, "message": "Could not lock the system."}

    def shutdown_system(self):
        return {
            "success": False,
            "message": "Computer shutdown is recognized, but disabled for safety."
        }
