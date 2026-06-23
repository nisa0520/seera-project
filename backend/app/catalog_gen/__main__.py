"""``python -m app.catalog_gen`` entry point."""
import sys

from app.catalog_gen.cli import main

if __name__ == "__main__":
    sys.exit(main())
