#!/usr/bin/python3
import traceback
import sys

from . import repl

def main() -> int:
	print("Feel free to type in commands")
	try:
		repl.Start(sys.stdin, sys.stdout)
		return 0
	except Exception as e:
		print (traceback.format_exc())
		return 1

if __name__ == "__main__":
	exit(main())
