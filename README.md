Dopplemaker - Patternmaking Software
------

Dopplemaker is an Inkscape Extension for patternmaking.  At its most basic level, it is a collection of python functions that make life easier for entering formulas to design and edit clothing patterns and blocks on Inkscape.  Patterns can be custom fit to a wearer's measurements or graded to standard measurements.  The program comes with standard measurements as well as  template for custom measures and measurements.  Included in the project are also several standard blocks and patterns that are ready for use.

Getting Started
------

* Dopplemaker is an Inkscape Extension and not a standalone program, so you must first install [Inkscape](http://www.inkscape.org/en/download/) on your computer.

* Each Dopplemaker extension relies on two initial files [sewing_patterns.py]() and [xmlparser.py]().  You must download these and place them in your Inkscape extensions diectory (most likely $HOME/.config/inkscape/extensions)

* In addition to these two files, each individual pattern or block comes with at least three more files of the format patternname_designer.py, patternname_designer.inx, and patternname_deisgner_msmnts.txt. These files should also be place in your extensions directory.  More about the individual patterns and blocks can be found in the [project wiki]().

* Once you have all of the files you desire in your extensions directory, you need to make the python files executable.  You do this by opening a terminal to the extensions directory and typing "sudo chmod *.py a*x".  The prompt will as for your password (you must have administrative privileges).

* Most likely you are now ready to go.  Open (or restart) Inkscape.  In you Extensions menu you should have a new submenu labeled "Sewing Patterns" and your patterns will be in available in the submenu.  Once you select a pattern you will be prompted to select a size or enter in your custom measurements.  Click "Apply" to see your pattern.

Possible Error with OSX Lion
------

Python Inkscape Extensions do not currently work under OSX Lion. There is an error proclaiming that lxml is not installed. An easy workaround is described in comment #7 on this page:  https://answers.launchpad.net/inkscape/+question/194132


Credits
------
Much of sewing_patterns.py was written by Susan Spencer at taumeta.org. I have just built upon it for my own needs and added my own custom blocks and patterns. She is now collaborating on another great project for standalone open source patternmaking software called [Valentina](https://bitbucket.org/dismine/valentina/overview). Valentina promises to be something really great and won't require programming knowledge.

Wiki
------
Please look at the wiki for pattern and block descriptions, tutorials on writing your own patterns, instructions on creating seam allowances, creating printable patterns, and more.