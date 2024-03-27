import subprocess
import time
import os
import keyboard  # You need to install this module

def is_user_root():
    # Retorna True si el UID efectivo es 0 (root), de lo contrario False
    return os.geteuid() == 0

# Verificar si el usuario es root
if not is_user_root():
    print("Este script debe ser ejecutado como usuario root.")
    exit(1)

def is_program_installed(program_name):
    try:
        # Intenta ejecutar el programa para verificar si está instalado
        subprocess.run([program_name, "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        # El programa no está instalado
        return False

# Verifica si xdotool está instalado
if not is_program_installed("xdotool"):
    print("Error: 'xdotool' no está instalado.\nPor favor, instálalo usando:\nsudo apt-get install xdotool")
    want_to_install = input("¿Quieres instalarlo ahora? (Solo funciona en distribuciones basadas en Debian) [s/N]: ").strip().lower()

    if want_to_install.lower() == "s" or want_to_install.lower() == "si":
        print("Instalando...")
        subprocess.run(["sudo", "apt", "install", "xdotool"])
        print("Instalado")
    else:
        print("Instalación omitida.")
        exit()

def get_pid(process_name):
    try:
        pid = subprocess.check_output(["pgrep", "-f", process_name]).decode().strip().split('\n')[0]
        return pid
    except subprocess.CalledProcessError:
        print(f"No process found with name '{process_name}'.")
        return None

def send_signal(pid, signal):
    subprocess.run(["kill", f"-{signal}", str(pid)], check=True)

def mouse(action:str):
    if action == "hold":
        subprocess.run(["xdotool", "mousedown", "1"])
    elif action == "release":
        subprocess.run(["xdotool", "mouseup", "1"])
    elif action == "click":
        subprocess.run(["xdotool", "mousedown", "1"])
        time.sleep(0.1)
        subprocess.run(["xdotool", "mouseup", "1"])

# Get the process name and PID
process_name = input("Enter the process name: ")
pid = get_pid(process_name)
if pid is None:
    exit(1)


# Time in seconds to stop and continue the process
sleep_time = 0.02
sleep_period = 0.06

# Loop control flag
continue_speedhack = True
continue_autoclicker = False

try:
    while True:
        # Check if 'F1' was pressed to pause speedhack
        if keyboard.is_pressed('F1'):
            if continue_speedhack:
                continue_speedhack = False
            else:
                continue_speedhack = True

        # Check if 'F2' was pressed to pause autoclicker
        if keyboard.is_pressed('F2'):
            if continue_autoclicker:
                continue_autoclicker = False
            else:
                continue_autoclicker = True

        if continue_speedhack:
            # Stop the process
            send_signal(pid, "SIGSTOP")

            # Wait
            time.sleep(sleep_period)

            # Continue the process
            send_signal(pid, "SIGCONT")

        if continue_autoclicker:
            # Hold
            # mouse("hold")		# Uncomment when fixed

            # Wait
            time.sleep(sleep_period)

            # Release
            mouse("release")

        # Wait
        time.sleep(sleep_time)

except KeyboardInterrupt:
    pass  # Handle Ctrl+C gracefully

# Ensure the process is continued before exiting the script
send_signal(pid, "SIGCONT")
