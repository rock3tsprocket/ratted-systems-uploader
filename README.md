# Set-up:

1. Clone this repository (`git clone https://github.com/rock3tsprocket/ratted-systems-uploader -b python2.7`).
2. Install the dependencies in a virtual environment with `python2 -m pip install requirements.txt`.
3. Rename the file named "config.example.json" to "config.json" and put your upload key in it.
4. (optional) Link the file to somewhere in your PATH (`ln -s [path to uploader.py] ~/bin` (Make sure to add ~/bin to your PATH if you're following this specific example)).

# How to use:

* Upload a file with `./uploader.py --upload [PATH]`.
