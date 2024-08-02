# Notebook

# Links
- blender addon dev env
    - https://blenderartists.org/t/share-your-addons-development-environment/1332819
    - https://polynook.com/learn/set-up-blender-addon-development-environment-in-windows#dealing-with-the-python-is-not-installed-popup

- blender chat
    - https://blender.chat/channel/python
    - https://blender.chat/channel/blender-coders
- docs blender
    - https://developer.blender.org/docs/handbook/addons/
- blender developer
    - https://developer.blender.org/
- dev forum
    - https://devtalk.blender.org/
- projects to start
    - https://projects.blender.org/blender/blender/issues?labels=302
- bpy docs
    - https://docs.blender.org/api/current/index.html
- sharing python code
    - https://bpa.st/
- blender 4.2 manual    
    - https://docs.blender.org/manual/en/latest/advanced/scripting/addon_tutorial.html
- how to think like cs
    - https://runestone.academy/ns/books/published/thinkcspy/index.html


# Setting up environment
- install blender
- install python
- install vsc
    - addon: blender development by jacques lucke
    - addon: python              by microsoft
- install fake bpy module 
    - https://github.com/nutti/fake-bpy-module
    - pip install fake-bpy-module-latest
        - & "D:\SteamLibrary\steamapps\common\Blender\4.2\python\bin\python.exe" --% -m pip install fake-bpy-module-latest --user
        - add auto complete path
            - file > prefs > settings
                - search: auto complete
                - python auto complete extra paths:
                    - "<path-to-generated-modules>" add
        - set py interpreter f1 > interpreter 
            - python in blender path
            - f1 > reload 
- cd addon file
    - py -m venv .venv
    - act: .\.venv\scripts\activate
- to reload on save: file > pref > settings: blender reload: thick

# Packages
- install python and pip | 
    - check: py --version
    - check: pip --version
    - https://medium.com/@viknesh2798/how-to-fix-the-issues-while-using-python-command-in-the-command-prompt-ba56d9018c5f

- python -m ensurepip --upgrade
- py -m pip install --upgrade pip

# Recommendations
- flake8 tool for style
- 4 space indentation

# Keywords

# Structure

# Blackboard
- <what is linter>
    - A linter is a program that checks your code for syntax and style errors and highlights them.

- <utility>
    - blender > interface > activate: python tooltips
    - blender > interface > acyivate: developer extrass
    - blender > window > toggle system console (for printing)
    - enable addon: 

- <Roadmap>
    - [ ] auto reload
        - q: Hello I am new at blender addon scripting, using python 3.12 and blender version 4.2.0. I am trying to build an efficient development environment. I am using external text editor, and it takes too much time to click resolve conflicts on blender and run the script again.

        Trying to create an auto-script reloader that checks every second the changes on the main script file. Check is successful, run working without a problem but, I have problem with updating the code in blender text editor. I am seeking for any guidance on how to solve it. Thanks in advance

    - [ ] multiple file structure addon
        - https://stackoverflow.com/questions/64796854/how-to-make-a-blender-addon-with-multiple-folders

    - [x] Material overlay
        - enable disable
        - uv map
        - custom material
        - toon shader

    - outlines
        - outside thickness
        - inner line thickness

    - focus on outliner viewport selected object
        - when cursor is on outliner press dot on the numpad

    - create default scene

# How to
- <blender community channels>
    - libera irc blenderchat
    - blender self blenderchat
    - discord blender scripting
    - blender reddit
    - blender stack exchange

- <how to identify a function> 
    - 

- <reload script on multiple file addon | addon reloading>
    - https://projects.blender.org/blender/blender-manual/issues/67387
    - failed
        - https://projects.blender.org/blender/blender/issues/113644
    - fixed 
        - https://projects.blender.org/blender/blender/issues/113644
    - load addon
    - f3 > reload scripts


# Problems
- <attempted relative import with no known parent package>
    - 

# How to

