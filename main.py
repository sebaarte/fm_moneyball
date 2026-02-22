import sys
import os

# Add frontend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'frontend'))

from frontend.gui import main

if __name__ == "__main__":
    main()