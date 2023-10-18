import sys

from ._create import main

if __name__ == "__main__":
    if sys.platform == "win32":
        print("Microvenv's CLI is not supported on Windows", file=sys.stderr)
        sys.exit(1)

    main()
