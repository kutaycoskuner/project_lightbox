# Notebook

# Links
- example project
    - bakernode addon
        - https://github.com/avelgest/baker-node

- css sketched line
    - https://stackoverflow.com/questions/43694588/can-i-use-css-to-distort-borders-so-they-look-like-sketched
    - https://github.com/chr15m/DoodleCSS

- https://shields.io/badges

- badges / shields
    - https://shields.io/badges/static-badge
    - https://simpleicons.org/?q=discord
    - https://github.com/simple-icons/simple-icons/blob/master/slugs.md

- readme example
    - https://github.com/Griperis/BlenderDataVis?tab=readme-ov-file
    - https://github.com/telegramdesktop/tdesktop/blob/dev/README.md

- blender addon dev env
    - https://blenderartists.org/t/share-your-addons-development-environment/1332819
    - https://polynook.com/learn/set-up-blender-addon-development-environment-in-windows#dealing-with-the-python-is-not-installed-popup

- node preview in shader editor project
    - https://projects.blender.org/blender/blender/pulls/109120

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

- bpy_struct ImagePreview
    - https://docs.blender.org/api/current/bpy.types.ImagePreview.html

# Structure
lightbox/
-   abstract/
    - nodehasher.py
-   panels/
-   operators/
    -  __init__.py
    -  module1.py
    -  module2.py
-  shortcuts/
    -  __init__.py
-  __init__.py

# Naming convention
    - prefix _ is to indicate private

# Setting up environment
- install env
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

- extra install
    - pip install numpy

- run
    - cd lightbox
    - activate environment
    - f1 > start blender

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
- bpy.types.shader.outputs


# Blackboard
- <naming convention>
    - pt -> panel type
    - ot -> object type
    - mt -> ? menu type

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
- <add operator>
    - add to init in ops/
    - add .py 
    - change name, label
    - add in panel
    - add in keys
    - add logic

- <change linting rules for python>
    - flake8
    - ctrl+,
        - search edit in settings
        - add: "flake8.args": ["--max-line-length=91"]


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


- <redsquare to texture>
    - invoke : shaderi uniform colordan image a 
    - draw_callback:
        - remove disable uniform_float
        - in: self.draw_square

# Problems
- <accessing shader editor zoom level>
    - https://blenderartists.org/t/node-editor-zoom-level/1478930/2

- <class fonksiyonunu disaridan cagirma>
    - see. node_ot_previewdrawer
    - global instance obje yaratinca global array icine at
    - staticte loop yaptirip cleanup calistir

- <attempted relative import with no known parent package>
    - development environmenti degistirerek cozdum

- <ReferenceError: StructRNA of type Node_OT_PreviewDrawer has been removed>
    - debugging ile cozdum
    - yeni fix | modal yeniden loopa sokuyor. Loop icinde objeyi bulamayinca problem yasiyor.
        - disaridan erisebilecek bir callback fonksiyonu yaratip loopu kirdiracak bir degiskeni degistiren fonksiyon cancel yaptim.
        - degistrationdan once bu fonksiyonu cagiriyor
    1. structa acip nerede soruna girdigine dair parametreleri inceledim.
    2. hicbir zaman callback idrawdan kaldiramiyor cunku self reference errore dusuyor
    3. handler a global referans verip ekleyerek. unregisterda iptal ettim.

- <wm_operator_invoke: invalid operator call NODE_OT_draw_squares>
    - self.layout.operator("node.draw_squares")
    - solution: class def requires execute method.
    - https://blender.stackexchange.com/questions/7085/error-in-addon-wm-operator-invoke-invalid-operator-call


# How to

# Analysis
- bakernode
    - command pattern
        - komutlari dogrudan cagirmak yerine opcaller adinda bir sinif uzerinden soyutlayarak cagiriyor. Bu api degistirince kodu tek yerden degistirme imkani sagliyormus.
    - queue class
        - jobqueue
    - hash serializer
        - her karede renderlamak icin ne zaman update edecegini belirlemek icin node degisimlerini baz alaarak hash atiyor. hash degistiyse yeniden renderliyor



