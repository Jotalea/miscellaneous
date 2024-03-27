available_pkgs = ["neofetch", "pyos"]

def main(argument, package=""):
    if argument == "search":
        for package in available_pkgs:
            print(package)
        return