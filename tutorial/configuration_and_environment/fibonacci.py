import argparse
import os

parser = argparse.ArgumentParser(description="Fibonacci printer")
parser.add_argument("n",
                    type=int,
                    help="The max rank of the fibonacci sequence to write")
parser.add_argument("--filename",
                    type=argparse.FileType('w'),
                    help="The file to write to",
                    default=os.environ.get("FIBO_FILE_PATH"))


def fibonacci_sequence(n: int = 0):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b


if __name__ == "__main__":
    args = parser.parse_args()
    with args.filename as f:
        for v in fibonacci_sequence(args.n):
            f.write(f"{v}\n")
