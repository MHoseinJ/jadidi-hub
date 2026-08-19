import sys

from src import cli


def main():
    args, arg_count = cli.get_args()
    return cli.parse_args(args, arg_count)


if __name__ == "__main__":
    sys.exit(main())