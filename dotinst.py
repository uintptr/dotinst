#!/usr/bin/env python3

import os
import sys
import json
import glob
import shutil
import argparse


def printkv(k: str, v: object) -> None:

    k = f"{k}:"
    print(" " * 4 + f"{k:<20} {v}")


def is_posix() -> bool:
    return "win32" != sys.platform


def install_links(config: str, src: str, dst: str, verbose: bool) -> None:

    plat = sys.platform

    with open(config) as f:
        files = json.load(f)

    for f in files:

        plat = sys.platform

        src_path = os.path.join(src, f)

        if False == os.path.exists(src_path):
            raise FileNotFoundError(src_path)

        if plat not in files[f]:

            if is_posix() and "posix" in files[f]:
                plat = "posix"
            elif "any" in files[f]:
                plat = "any"
            else:
                continue

        dest_spec = files[f][plat]

        if isinstance(dest_spec, str):
            dest_files = [dest_spec]
        elif isinstance(dest_spec, list):
            dest_files: list[str] = dest_spec
        else:
            raise ValueError("Unknown format")

        for f in dest_files:
            dst_path = os.path.join(dst, f)

            # normalize
            dst_path = os.path.abspath(dst_path)

            if True == verbose:
                print(f"{dst_path} --> {src_path}")

            dst_dir = os.path.dirname(dst_path)

            if False == os.path.exists(dst_dir):
                os.makedirs(dst_dir)

            if True == os.path.isfile(dst_path):
                os.unlink(dst_path)
            elif True == os.path.islink(dst_path):
                os.unlink(dst_path)
            elif True == os.path.isdir(dst_path):
                shutil.rmtree(dst_path)
            os.symlink(src_path, dst_path)


def find_config_files(src: str) -> list[str]:

    patt = os.path.join(src, "**", "dotinst.json")
    return glob.glob(patt, recursive=True)


def main() -> int:

    status = 1

    parser = argparse.ArgumentParser()

    def_src = os.getcwd()
    def_dst = os.path.expanduser("~/")

    parser.add_argument("-v",
                        "--verbose",
                        action="store_true",
                        help="Verbose")

    parser.add_argument("-s",
                        "--source",
                        type=str,
                        default=def_src,
                        help=f"Source directory. Default: {def_src}")

    parser.add_argument("-d",
                        "--dest",
                        type=str,
                        default=def_dst,
                        help=f"Destination directory. Default: {def_dst}")

    args = parser.parse_args()

    try:

        args.source = os.path.abspath(args.source)
        args.dest = os.path.abspath(args.dest)

        print("dot installer:")
        printkv("Source", args.source)
        printkv("Destination", args.dest)

        if False == os.path.exists(args.source):
            raise FileNotFoundError(args.source)

        if False == os.path.exists(args.dest):
            raise FileNotFoundError(args.dest)

        for c in find_config_files(args.source):
            install_links(c, args.source, args.dest, args.verbose)

        status = 0

    finally:
        pass

    return status


if __name__ == '__main__':

    status = main()

    if 0 != status:
        sys.exit(status)
