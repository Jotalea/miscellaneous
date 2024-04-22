// JotaleaOS - An OS simulator, not to be taken seriously, made for practicing C++

#include <iostream>

void commandHelp() {
    std::cout << "List of all commands\nWHOAMI - Displays the current user\nHELP - Shows this list" << std::endl;
}

void commandWhoami(std::string user) {
    std::cout << user << std::endl;
}

void commandExit() {
    std::cout << "Bye bye" << std::endl;
}

int main() {
    std::string user = "";
    std::cout << "Log in: ";
    std::cin >> user;

    std::cout << "Welcome " << user << " to JotaleaOS" << std::endl;

    std::string command = "";

    while (true) {
        std::cout << "/Users/" << user << "/: ";
        std::cin >> command;
        if (command == "") {
            std::cout << std::endl;
        } else {
        if (command == "help") {
            commandHelp();
        } else {
            if (command == "whoami") {
                commandWhoami(user);
        } else {
            if (command == "exit") {
                commandExit();
                return 0;
        } else {
            std::cout << "jotashell: program " << command << " not found" << std::endl;
        }
        }
        }
        }
    }
}
