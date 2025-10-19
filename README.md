# Set-up:

1. Clone this repository (`git clone https://github.com/rock3tsprocket/ratted-systems-uploader`).
2. Install the dependencies in a virtual environment with `python -m pip install requirements.txt` or `sudo apt install python3-requests`.
3. Rename the file named "config.example.json" to "config.json" and put your upload key in it.
4. (optional) Link the file to somewhere in your PATH (`ln -s [path to uploader.py] ~/bin` (Make sure to add ~/bin to your PATH if you're following this specific example)).

# How to use:

* Upload a file over HTTPS with `./uploader.py --upload [PATH]`.
* Upload a file over WebSockets with `./uploader.py --uploadws [PATH]`.
* Get verbose output out of `--uploadws` with the `-v` or `--verbose` arguments.

# Xfce Screenshooter integration (requires Zenity):

1. Open xfce4-screenshooter (for example, by pressing Print Screen) and click "Preferences".
2. Click the + button.
3. Type any name you want in the "Name" textbox.
4. In the "Command" box, type `[PATH TO UPLOADER] --upload %f`.
5. When you screenshot something, select the "Custom Action" dropdown menu and select the option you just added.
6. Profit.
