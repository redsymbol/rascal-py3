#!/usr/bin/env python3
from rascal import main

def get_args():
    import argparse
    parser = argparse.ArgumentParser(
        description='Rascal - toy roguelike game',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        )
    return parser.parse_args()

if __name__ == '__main__':
    main(get_args())
