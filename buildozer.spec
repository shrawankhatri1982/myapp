[app]
# App details
title = SADANAND COMPUTERS
package.name = sadanand_computers
package.domain = org.sadanand
source.dir = .
source.include_exts = py,kv,png,jpg,db,csv,ttf
version = 0.1
requirements = python3,kivy==2.1.0,kivymd,sqlite3
orientation = portrait

# Icon (optional - अगर icon.png है तो use होगा, वरना default रहेगा)
icon.filename = %(source.dir)s/icon.png

# Permissions
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,INTERNET

# Entry point (तुम्हारी main file का नाम)
entrypoint = main.py


[buildozer]
log_level = 2
warn_on_root = 1

[android]
android.api = 33
android.minapi = 24
