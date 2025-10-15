# Building guide

## Prerequisites:
- libcurl (most likely `libcurl` in your distro's repository).
- Any C compiler as long as it's compatible with C89 or later.

## Instructions:
1. Configure the build by running `./configure`.
2. Build ratted-systems-uploader by running `make`.
- If you want, you can copy it to somewhere in $PATH and run it by just typing `uploader` in a shell.
- You can regenerate the `configure` script by running `autoconf` if you have that installed.
