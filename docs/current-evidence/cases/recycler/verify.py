"""Archive-root compatible entry point for the Recycler portable check."""

import sys

sys.dont_write_bytecode = True

from verify_case import main


if __name__ == "__main__":
    main()
