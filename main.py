import sys
from jarvis.ui.interface import JarvisUI

def main():
    print("Launching Jarvis UI...")
    app = JarvisUI()
    app.mainloop()

if __name__ == "__main__":
    main()
