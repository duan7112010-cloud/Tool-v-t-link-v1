[app]
title = Link Resolver
package.name = linkresolver
package.domain = org.example

source.dir = .
source.include_exts = py

version = 0.1

# requests cần đủ các thư viện đi kèm thì mới chạy được trên Android
requirements = python3,kivy==2.3.0,requests,urllib3,idna,certifi,charset-normalizer

orientation = portrait
fullscreen = 0

android.permissions = INTERNET
android.api = 33
android.minapi = 24
android.archs = arm64-v8a
android.accept_sdk_license = True
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
