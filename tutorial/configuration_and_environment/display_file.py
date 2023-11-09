import argparse
import os

parser = argparse.ArgumentParser(description="File printer")
parser.add_argument("--filename",
                    type=argparse.FileType('r'),
                    help="The file to print",
                    default=os.environ.get("FIBO_FILE_PATH"))

if __name__ == "__main__":
    args = parser.parse_args()

    with args.filename as f:
        for v in f.readlines():
            print(v.strip())
