This Python script lets you upload to https://ratted.systems without using ShareX (if you're whitelisted).

# Set-up:

1. Clone this repository (git clone https://github.com/rock3tsprocket/ratted-systems-uploader)
2. Install the dependencies in a virtual environment with `python -m pip install requirements.txt` or `sudo apt install python3-{requests,dotenv}`
3. Rename the file named "example.env" to .env and put your Discord token (or Ratted Systems upload key) in it.
4. (optional) Link the file to somewhere in your PATH (`ln -s [path to uploader.py] ~/bin` (Make sure to add ~/bin to your PATH if you're following this example specifically))

# How to use:

* Upload a file with `./uploader.py --upload [PATH]`

* List the files that you have uploaded with `./uploader.py --list`

* Delete a file that you have uploaded with `./uploader.py --delete [FileName (NOT OriginalFileName in the list)]`
