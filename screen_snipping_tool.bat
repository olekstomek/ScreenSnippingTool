CD %~dp0
SET QT_QPA_PLATFORM_PLUGIN_PATH=D:\ProgramFiles\Qt\Qt-5\5.11.1\msvc2017_64\plugins
SET PATH=D:\ProgramFiles\TesseractOCR;%PATH%
D:\ProgramFiles\Python\Anaconda-x64\pythonw.exe screen_snipping_tool.py -o "ScreenSnippingImages/ScreenSnippingImage_%%Y-%%m-%%d_%%H-%%M-%%S.png" -l screen_snipping_tool.log -s 1000 -d 1
