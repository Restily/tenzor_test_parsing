import sys

from parser import Parser


if __name__ == '__main__':
    parser = Parser()
    parser.start(sys.argv[1])