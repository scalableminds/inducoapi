#!/usr/bin/env python3

#  Copyright 2020 Matteo Pergolesi <matpergo [at] gmail [dot] com>
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import argparse
import sys

import yaml
from openapi3.errors import SpecError

from .inducoapi import build_openapi


class _NoAliasDumper(yaml.Dumper):
    def ignore_aliases(self, data):
        return True


def _get_parser():
    descr = "A simple python program to generate OpenApi documentation by " \
            "supplying request/response bodies"
    fmt = argparse.ArgumentDefaultsHelpFormatter
    usage = "%(prog)s METHOD PATH CODE [options]"
    p = argparse.ArgumentParser("inducoapi.py", description=descr,
                                usage=usage, formatter_class=fmt)
    p.add_argument("method", type=str,
                   choices=["GET", "POST", "PUT", "PATCH", "DELETE"],
                   metavar="METHOD",
                   help="HTTP request method")
    p.add_argument("path", type=str, metavar="PATH",
                   help="URI path")
    p.add_argument("resp_code", type=int, metavar="CODE",
                   help="HTTP response code")
    p.add_argument("-req", "--request", type=str, metavar="PATH",
                   help="Path to file containing request body")
    p.add_argument("-resp", "--response", type=str, metavar="PATH",
                   help="Path to file containing response body")
    p.add_argument("-o", "--output", type=str, metavar="PATH",
                   help="Path to output file")
    p.add_argument("-mt", "--media-type", type=str, metavar="STR",
                   default="application/json",
                   help="Desired media type to be used")
    p.add_argument("-ne", "--no-example", action="store_false", dest="example",
                   default=True,
                   help="Do not generate schema examples")
    p.add_argument("-it", "--info-title", type=str, metavar="STR",
                   default="Generated by InducOapi",
                   help="The title to be used in the 'info' field")
    p.add_argument("-iv", "--info-version", type=str, metavar="STR",
                   default="v1",
                   help="The version to be used in the 'info' field")
    return p


def main():
    args = _get_parser().parse_args()

    if args.request:
        try:
            with open(args.request) as f:
                request = f.read()
        except OSError as e:
            sys.exit(f"Error reading request file\n{e}")
    else:
        request = None

    if args.response:
        try:
            with open(args.response) as f:
                response = f.read()
        except OSError as e:
            sys.exit(f"Error reading response file\n{e}")
    else:
        response = None

    try:
        oapi = build_openapi(args.method, args.path, args.resp_code,
                             request=request, response=response,
                             media_type=args.media_type, example=args.example,
                             title=args.info_title, version=args.info_version)
    except SpecError as e:
        sys.exit(f"OpenAPI validation error\n{e}")
    except ValueError as e:
        sys.exit(f"{e}")

    dump_kwds = {"indent": 2, "Dumper": _NoAliasDumper, "sort_keys": False}
    if args.output:
        try:
            with open(args.output, "w") as o:
                yaml.dump(oapi, o, **dump_kwds)
                print(f"Output written to {args.output}")
        except OSError as e:
            print(f"Error writing output file\n{e}")
    else:
        print(yaml.dump(oapi, **dump_kwds))


if __name__ == "__main__":
    main()
