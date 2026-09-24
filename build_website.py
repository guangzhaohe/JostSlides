"""Compatibility command; prefer `python slides.py build [--deck YYYY-MM-DD]`."""
import sys
from slides import main
if __name__ == '__main__':
    main(['build', *sys.argv[1:]])
