#!/usr/bin/env python
"""The main entry point.
Invoke as `fastensource' or `python -m fastensource'.
"""
import sys
from fastensource.cli import get_parser


def main():
    parser = get_parser()
    args = parser.parse_args()
    #  try:
    # execute the appropriate command
    args.func(args)
    #  except AttributeError:
        #  parser.print_help(sys.stdout)


if __name__ == '__main__':
    main()
