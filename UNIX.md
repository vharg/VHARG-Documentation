# General UNIX concepts

UNIX (here used as a synonym of Linux) is a *command line-based* operating system. The same tasks can be achieved as with a *Graphical User Interface* (GUI) but through text commands. To access it, use the `Powershell` on Windows and `Terminal` on MacOS. This intro is a rough guide to illustrate the most useful commands to get started, but remember that Google Sensei is here for you too!

## General concepts
Here are some general concepts that are applicable throughout this guide:
1. In UNIX environments, paths are defined using a forward slash `/`. This is the same as with MacOS, but bear in mind that it differs from Windows, which uses back slashes `\` instead;
2. *Commands* refer to actions that you, as the end-user, kindly request your computer to perform. The command is the main action you request from the computer, but these actions can be customised and refined by using *arguments*. Arguments are usually passed after the command, for instance:

```
>> command argument1 argument2
```
That will hopefully become clearer as we go. Bottom line is see your computer as someone you can communicate with through a strictly-defined language. If the language you use is propererly structured, the computer will perform the requested tasks very accuratly. Alternatively, the computer cannot understand approximations of language, and vague commands won't be understood.

### Autocomplete
The `Tab` key is a time-saver in UNIX. It allows to auto complete what you type, be it commands or paths. For instance, type `sor` and press `Tab` - that should auto-complete to the command `sort`. Now type `ca` and press `Tab`. Nothing happens? That is because more than one command start with `ca`. Now press the `Tab` key twice and it will display all commands starting by `ca`. Add `len` (to have `calen`) and press Tab, that should autocomplete to `calendar`. 

- :warning: If a command is stuck, the magic key to interupt it is **ctrl+c**
- :warning: There is no recycled bin in UNIX, so be careful when you delete something


## Finding your way around files and folders
UNIX usually lands you in your `HOME` folder - the rough equivalent of you `Documents` folder on Windows/Mac. At any time, you can use the `pwd` command to print the current directory and `ls` to print the content of the directory. See that as the equivalent of the Explorer/Finder window.

The command `ls` will list everything in your directory, but it is also possible to filter that by using a *wildcard*, which is the symbol `*`. For instance, `ls *.txt` lists all files with the extension `.txt`, and `ls dog*` lists all files that start with `dog`, which could include `dog.txt` or `dogRed.csv`. 

The main command to navigate in and out of sub-directories is `cd`. `cd myDir` enters the directory named `myDir` whereas `cd ..` goes back one directory. Use `cd ../..` to go back two directories. 

### Examples
```
ls -h                   # Lists current directory
ls -h myDir             # Lists the content of myDir
ls -h myDir/*.txt       # Lists all text files in myDir
cd myDir                # Navigates to myDir
cd myDir/mySubDir       # Navigates to mySubDir
cd ~                    # Navigates back to the home folder
```


## Interacting with files and folders
You can create a new directory named `myDir` by using the command `mkdir myDir`. Using commands from the previous sections, you can now:
- List the content of `myDir` with `ls myDir`
- Go into `myDir` with `cd myDir`, or type `cd my` and press the `Tab` key

The general *delete* command is `rm`. You can remove an empty directory with the command `rmdir myDir`. If the directory contains files, you need to use `rm -r myDir`. `-r` is an argument that generally means *recursive*, which means that everything contained within the directory will be deleted. It won't ask you whether you are sure or not, so :warning:**use carfully!!!**:warning:. Both Prof. Jenkins and Dr. Biass have stupidly lost their data with the improper use of this command at late hours of the night.

The general *copy* command is `cp`. To copy files to a new location, use `cp original.txt duplicate.txt`. To copy directories, use `cp -r originalDir duplicateDir`. The general *cut* command is `mv` (for move), which is used exactly as `cp`.

```
mkdir myDir                                     # Creates directory myDir
mkdir myDir/mySubDir                            # Creates directory mySubDir in myDir
rm -r myDir                                     # Deletes myDir and its content
cp file1.txt myDir/file2.txt                    # Duplicates file1.txt to myDir/file2.txt
mv myDir/file2.txt myDir/mySubDir/file3.txt     # Moves files
```


## Editing ascii files
Most of the files used in the numerical models are ascii files, meaning they are files that can be edited with a text editor. For having a look at a file withouth editing capapbilities, use the command `more`:
```
more file.txt
```

To edit files, the most powerful option is [VIM](https://en.wikipedia.org/wiki/Vim_(text_editor)), which is a pretty good cause for headache at the beginning. You can edit any file with:
```
vi file.txt
```

Vim has two main modes:
- The *command* mode allows navigating the file and sending commands such as *save* and *quit*. By default, Vim enters in *command* mode, and navigation through the file can be done with the keyboard arrows;
- The *insert* mode allows editing the file.

To enter the *insert* mode, type `i`. To escape back to the *command* mode, press `Esc`. To save or quit Vim, you must be back to the *command* mode, then the options are (press `Return` to confirm):
- `:w!`: Saves the file
- `:q!`: Exits Vim without saving the file
- `:x!`: Saves the file and exits Vim 


## Summary of useful commands

| Command | Action |
| ----- | -----|
| `pwd` | Prints the path of the current directory |
| `ls` | Lists the content of the current directory. `ls myDir` lists the content of the directory `myDir`. `ls -h` provides an easier display |
| `cd dir` | Enters the directory `dir` |
| `cd ..`  | Goes back one directory, use `cd ../..` to go back two directories |
| `cd ~` | Navigates back to the `$HOME` directory |
| `mkdir` | Creates a new directory |
| `rm` | Removes a file. Use `rm -r` to remove a directory and all its content |
| `cp` | Copies a file. Use `cp -r` to copy a directory and all its content|
| `mv`  | Moves a file or a directory |
