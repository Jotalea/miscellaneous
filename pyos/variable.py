# Initializing empty variables
cmd = ""
cmd_args = []
username = ""
password = ""

# Other variables
root = False
hostname = "computer"
pwd = "/"
dirs = ["/","/sbin","/bin"]
commands = ["exit", "pypm", "help", "ls", "read", "write"]
help_content = "Available commands:\nexit - Exits the simulator\npypm - Package manager\nhelp - Lists all the commands"
jotalogo = "     ██╗ ██████╗ ████████╗ █████╗ ██╗     ███████╗ █████╗ \n     ██║██╔═══██╗╚══██╔══╝██╔══██╗██║     ██╔════╝██╔══██╗\n     ██║██║   ██║   ██║   ███████║██║     █████╗  ███████║\n██   ██║██║   ██║   ██║   ██╔══██║██║     ██╔══╝  ██╔══██║\n╚█████╔╝╚██████╔╝   ██║   ██║  ██║███████╗███████╗██║  ██║\n ╚════╝  ╚═════╝    ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝\n"
pyos_logo = """`7MM\"\"\"Mq.              .g8""8q.    .M\"\"\"bgd \n  MM   `MM.           .dP'    `YM. ,MI    "Y \n  MM   ,M9 `7M'   `MF'dM'      `MM `MMb.     \n  MMmmdM9    VA   ,V  MM        MM   `YMMNq. \n  MM          VA ,V   MM.      ,MP .     `MM \n  MM           VVV    `Mb.    ,dP' Mb     dM \n.JMML.         ,V       `"bmmd"'   P"Ybmmd"  \n              ,V                             \n           OOb"                              \n"""

cgpt_suggestions = """
It looks like you're working on a console simulator with a package manager feature. Here are some suggestions to enhance your console simulator:

    Command Validation:
        Validate the user's input command and provide appropriate error messages for invalid commands or syntax errors.

    Help Command:
        Implement a help command (help or similar) to provide users with information about available commands and their usage.

    Change Directory Command:
        Implement a cd command to change the current working directory. This can be useful for navigating through the simulated file system.

    List Directory Contents:
        Add a command (e.g., ls or dir) to list the contents of the current directory.

    Environment Information:
        Allow the user to view information about the environment, such as the current user, hostname, and working directory.

    Exit Command:
        Implement an exit or quit command to gracefully exit the console simulator.

    Customizable Prompt:
        Allow users to customize the console prompt. For example, let them change the format or include additional information.

    File System Operations:
        Extend the simulator to support basic file system operations, such as creating, deleting, and editing files and directories.

    Command History:
        Implement a command history feature, allowing users to navigate through previous commands using arrow keys or a dedicated command.

    Autocompletion:
        Add an autocompletion feature to suggest or complete command and file/directory names as the user types.

    User Authentication:
        Introduce a basic user authentication system with different user roles (e.g., regular user and root/administrator).

    Package Installation/Management:
        Extend the package manager functionality to include commands for installing, updating, and removing packages.
"""

jlogo1 = """
    ....::::::   ...   :::::::::::::::.      :::    .,::::::   :::.     
 ;;;;;;;;;````.;;;;;;;.;;;;;;;;'''';;`;;     ;;;    ;;;;''''   ;;`;;    
 ''`  `[[.   ,[[     \[[,   [[    ,[[ '[[,   [[[     [[cccc   ,[[ '[[,  
,,,    `$$   $$$,     $$$   $$   c$$$cc$$$c  $$'     $$\"\"\"\"  c$$$cc$$$c 
888boood88   "888,_ _,88P   88,   888   888,o88oo,.__888oo,__ 888   888,
"MMMMMMMM"     "YMMMMMP"    MMM   YMM   ""` \"\"\"\"YUMMM\"\"\"\"YUMMMYMM   \"\"` 
"""

jlogo1 = """
 ▄▄▄██▀▀▀ █████  ▄▄▄█████  ▄▄▄       ██      █████ ▄▄▄      
    ██   ██   ██    ██     ████▄     ██      █   ▀ ████▄    
    ██   ██   ██    ██     ██  ▀█▄   ██      ███   ██  ▀█▄  
 ██▄██   ██   ██    ██     ██▄▄▄▄██  ██       █  ▄ ██▄▄▄▄██ 
  ███     ████      ██      █    ██  ██████   ████  █    ██ 
                                  █                       █
"""

jlogo1 = """
     ██╗ ██████╗ ████████╗ █████╗ ██╗     ███████╗ █████╗ 
     ██║██╔═══██╗╚══██╔══╝██╔══██╗██║     ██╔════╝██╔══██╗
     ██║██║   ██║   ██║   ███████║██║     █████╗  ███████║
██   ██║██║   ██║   ██║   ██╔══██║██║     ██╔══╝  ██╔══██║
╚█████╔╝╚██████╔╝   ██║   ██║  ██║███████╗███████╗██║  ██║
 ╚════╝  ╚═════╝    ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝
"""

jlogo1 = """
   █████\            ██\               ██\                     
   \__██ |           ██ |              ██ |                    
      ██ | ██████\ ██████\    ██████\  ██ | ██████\   ██████\  
      ██ |██  __██\\\\_██  _|   \____██\ ██ |██  __██\  \____██\ 
██\   ██ |██ /  ██ | ██ |     ███████ |██ |████████ | ███████ |
██ |  ██ |██ |  ██ | ██ |██\ ██  __██ |██ |██   ____|██  __██ |
\██████  |\██████  | \████  |\███████ |██ |\███████\ \███████ |
 \______/  \______/   \____/  \_______|\__| \_______| \_______|
 """