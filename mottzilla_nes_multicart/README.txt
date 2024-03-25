MultiCart 11-in-1 Loader
Programmed By: MottZilla

Quick Overview:
This software allows you to compile 11 Mapper 0 (NROM) games into one MMC-1 ROM. You could
use this to build your own MultiCart.

Included are MultiCart.exe and MultiCart.nes. The executable is a very simple Win32 program
and should be no trouble running it via emulation on another OS. MultiCart.nes is an EMPTY
cartridge image. No games are provided. By using MultiCart.exe you can insert your own games
into the cartridge image.

Usage:
MultiCart.exe is a command line program. You would use it by typing a command like this one.

MultiCart.exe "Super Mario Bros.nes" 3 "Super Mario Bros."

The first parameter, "Super Mario Bros.nes" is the filename of the game you wish to add.
The second, 3, is the slot number you want to put it in. 1 through 11 are valid slots.
The final parameter, "Super Mario Bros." is the title to appear on the menu for the game.

For the filename and title you MUST use quotes if you have any spaces in the string. If you
use spaces it will think that is the end of that parameter.

Limitations:
Only NROM (mapper 0) is supported. Also, if a game writes to PRG-ROM or CHR-ROM there is
nothing to prevent it from modifying MMC1 registers and crashing. Or in the case of CHR-ROM
it could actually modify the patterns. In the case of a mapper 0 game intended to use CHR-RAM
you should attach a dummy CHR-ROM page to it before trying to add it.
