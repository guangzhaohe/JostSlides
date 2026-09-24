"""Compatibility command; prefer `python slides.py export [--deck YYYY-MM-DD]`."""
import sys
from slides import main
if __name__ == '__main__':
    main(['export', *sys.argv[1:]])
