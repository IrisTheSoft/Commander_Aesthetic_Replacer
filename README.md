# Commander Aesthetic Replacer

This is a tool that generates mods for World of Warships that replace the name, portrait and voiceover of unique commanders. Its main use is to have the advantages of legendary commanders and a special voice over at the same time.

Custom names can be arbitrary, but do not exceed too much with their length and note that not all letters are supported by the vanilla in-game font.

For portraits it can use both official ones from the game and arbitrary files. If you are providing them, make sure that the aspect ratio is approximately 160:147 or they will look stretched in-game. Recommended size is at least 160x147px.

All non-modded voice overs should be available for assigning them to another commander.

## Requirements

You need to place `wowsunpack.exe` (not distributed here) at the tool's root folder.

## Usage

When opening the GUI, you will be greeted by a file dialog. Select the folder World of Warships is installed. It should look something like `<<SOMETHING>>/World of Warships/bin/<<SOME_NUMBER>>`. Usually, the highest number is the one you want.

Then you will be prompted if you want automatic installation. Choosing "yes" will clean the game's `res_mods` folder, which can be undesirable if you have other mods installed. If choosing "no", after the tool finishes its job you will need to move the contents of the tool's `output` folder to the game's `res_mods`.

Next, the main window is shown. There you can configure the mod. Session is saved automatically when closing this window at any time. To add change(s) for a new commander, press the "add" button.

The first column ("Commander") refers to the recipient commander and the next 3 columns are the new values you want for them. To keep a value as it is, leave the input blank (or pick "(None)" in the case of voice over). You can empty the portrait input by clicking "select" and then closing the file dialog.

The form at the bottom includes additional options. In "language", pick the language you use in the game. The "voice mod name" will be the name of the mod in the in-game settings. You probably do not care about the "voice mod ID" (it is only used for naming a folder).

When you are ready, press the "install" button and wait. Once it changes to "success" you are free to close the window.

If you rejected auto installation, move the contents of the tool's `output` folder to the game's `res_mods` at this point.

Now launch the game. Go to `settings > audio > voice` and set "modification" to the name of your mod.

## Adding support for more recipient commanders

Out of the box, this tool supports the following commanders:

* Yamamoto Isoroku
* Günther Lütjens
* Luigi Sansonetti
* William F. Halsey Jr.
* Nikolay Kuznetsov
* Andrew Cunningham

To make it work with more recipients, you need to add a line to the `commanders.csv` file with 4 values, separated by commas:

* A name to find them in the GUI (helpful).
* Their translation ID (for supporting name changing). It can be looked up in the `<<WOWS_FOLDER>>/res/texts/<<YOUR_LANGUAGE>>/LC_MESSAGES/global.mo`. A third party program or library is required to read `.mo` files.
* Their portrait path (for supporting portrait changing). To find this, while the tool is running, browse the sub-folders in `working/gui/crew_commander/base`.
* Their voice ID (for supporting voice changing). This one can be tricky. If your commander already has a voice over, while the tool is running you can search the `working/banks/OfficialMods/<<MOD_NAME>>/mod.xml`, which can be opened with any text editor. Otherwise, you can test different values taking the other keys as hints, but I have yet to find an easier way.

## Restoring defaults

The tool restores the last session on start up. To prevent this, delete the `session.json` file.
