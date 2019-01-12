# Screen Snipping Tool

Press `Alt+PrintScreen` to save and optionally show screen image.


## Usage

```
ScreenSnippingTool [-h] [-v] [-o OUTPUT] [-r] [-l LOG_FILE]
                          [-s SHOW_TIME]

Screen Snipping Tool

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -o OUTPUT, --output OUTPUT
                        The output file name pattern (default: 'ScreenSnipping
                        Images/ScreenSnippingImage_%Y-%m-%d_%H-%M-%S.png').
  -r, --override        Whether to override the output file if it exists
                        before.
  -l LOG_FILE, --log-file LOG_FILE
                        The log file name (default: log not saved).
  -s SHOW_TIME, --show-time SHOW_TIME
                        Milliseconds time to show the screen image (if 0, the
                        image won't be shown) (default: '1000').
  -d ASSIGN_DESCRIPTION, --assign-description ASSIGN_DESCRIPTION
                        Whether to assign description to the screen image (1
                        for manually input, 2 for OCR [NOT IMPLEMENTED],
                        others for no description) (default: '0').
  -b [BOUNDING_BOX [BOUNDING_BOX ...]], --bounding_box [BOUNDING_BOX [BOUNDING_BOX ...]]
                        [tuple] The image rectangle in screen, enter
                        dimensions by entering numbers e.g -b 150 200 300 400
```
