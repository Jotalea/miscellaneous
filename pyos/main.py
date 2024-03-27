from pypm import main as pypm
import variable

def main():
    import os
    os.makedirs(os.path.join(os.path.dirname(__file__), "disk"), exist_ok=True)

    print(variable.pyos_logo)
    
    if not variable.username:
        print("Log in")
    while not variable.username:
        variable.username = input("Username: ").lower().replace(" ", "")
    while not variable.password:
        variable.password = input("Password: ")

    variable.cmd = input(f"{variable.username}@{variable.hostname} [{variable.pwd}] $ ").lower()
    variable.cmd_args = variable.cmd.split(" ")

    # Debugging
    # print(variable.cmd_args)
    
    if variable.cmd:
        if variable.cmd_args[0] in variable.commands:
            pass
        else:
            print(f"Error: command {variable.cmd_args[0]} not found")

        if variable.cmd_args[0] == "exit":
            exit()

        elif variable.cmd_args[0] == "pypm":
            try:
                pypm(variable.cmd_args[1], variable.cmd_args[2])
            except IndexError:
                pypm(variable.cmd_args[1])

        elif variable.cmd_args[0] == "help":
            print(variable.help_content)

            

        elif variable.cmd_args[0] == "write":
            def write_to_file(filename, content):
                file_path = os.path.join(os.path.dirname(__file__), "disk", filename)
                with open(file_path, "w") as file:
                    file.write(content)

            if len(variable.cmd_args) == 3:
                filename = variable.cmd_args[1]
                content = variable.cmd_args[2]
                write_to_file(filename, content)
                print(f"File '{filename}' created successfully.")
            else:
                print("Error: writefile command requires a filename and content.")

        elif variable.cmd_args[0] == "read":
            def read_from_file(filename):
                file_path = os.path.join(os.path.dirname(__file__), "disk", filename)
                try:
                    with open(file_path, "r") as file:
                        return file.read()
                except FileNotFoundError:
                    return f"Error: File '{filename}' not found."

            if len(variable.cmd_args) == 2:
                filename = variable.cmd_args[1]
                file_content = read_from_file(filename)
                print(file_content)
            else:
                print("Error: readfile command requires a filename.")
        
        elif variable.cmd_args[0] == "ls":
            def list_files():
                disk_path = os.path.join(os.path.dirname(__file__), "disk")
                files = os.listdir(disk_path)
                return " ".join(files)
            print(list_files())

        return

try:
    while True:
        main()
    exit
except KeyboardInterrupt:
    exit()
