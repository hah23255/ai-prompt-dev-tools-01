import sys
import os

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app.run import check_lmstudio_running

if __name__ == "__main__":
    print(check_lmstudio_running())