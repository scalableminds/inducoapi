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
import json
from json import JSONDecodeError
from typing import Dict, Tuple, Any, Union, List

import yaml
from openapi3 import OpenAPI
from openapi3.errors import SpecError


def _get_type_ex(val: Any) -> Tuple[str, Any]:
    ex = val
    if val is None:
        # If no value is provided, assume string
        t = "string"
        ex = ""
    elif isinstance(val, str):
        t = "string"
    elif isinstance(val, int):
        t = "integer"
    elif isinstance(val, float):
        t = "number"
    elif isinstance(val, bool):
        t = "boolean"
    else:
        t = ""
        print("unknown type: {}, value: {}".format(type(val), val))
    return {
        "type": t,
        "example": ex
    }


def _gen_schema(data: Union[Dict, List]) -> Dict:
    if isinstance(data, dict):
        schema = {
            "type": "object",
            "properties": {}
        }
        for key, val in data.items():
            schema["properties"][key] = _gen_schema(val)
    elif isinstance(data, list):
        schema = {
            "type": "array",
            "items": {}
        }
        if data:
            schema["items"] = _gen_schema(data[0])
    else:
        schema = _get_type_ex(data)
    return schema


class NoAliasDumper(yaml.Dumper):
    def ignore_aliases(self, data):
        return True


def _get_parser():
    descr = "Simple script to generate OpenAPI block from JSON request/response"
    parser = argparse.ArgumentParser("json2openapi.py", description=descr)
    parser.add_argument("req_m", type=str,
                        choices=["GET", "POST", "PUT", "PATCH", "DELETE"],
                        help="HTTP request method")
    parser.add_argument("path", type=str, help="REST resource path")
    parser.add_argument("resp_code", type=int, help="Response code")
    parser.add_argument("--req-json", "-reqj", type=str,
                        help="Path to JSON file containing request body")
    parser.add_argument("--resp-json", "-respj", type=str,
                        help="Path to JSON file containing response body")
    parser.add_argument("--output", "-o", type=str, help="Output file")
    return parser


def main():
    args = _get_parser().parse_args()

    path = {
        args.path: {
            args.req_m.lower(): {
                "requestBody": {},
                "responses": {
                    args.resp_code: {
                        "description": "",
                        "content": None
                    }
                }
            }
        }
    }

    if args.req_json:
        with open(args.req_json) as req_json:
            try:
                req_body = json.load(req_json)
                path[args.path][args.req_m.lower()]["requestBody"] = {
                    "content": {
                        "application/json": {
                            "schema": _gen_schema(req_body)
                        }
                    }
                }
            except JSONDecodeError:
                print("JSON in {} looks not valid, skip request generation".
                      format(args.req_json))

    if args.resp_json:
        with open(args.resp_json) as resp_json:
            try:
                resp_body = json.load(resp_json)
                resp_content = {
                    "application/json": {
                        "schema": _gen_schema(resp_body)
                    }
                }
                path[args.path][args.req_m.lower()]["responses"][
                    args.resp_code]["content"] = resp_content
            except JSONDecodeError:
                print("JSON in {} looks not valid, skip response generation".
                      format(args.req_json))

    oapi = {
        "openapi": "3.0.0",
        "info": {
            "title": "Generated by json2openapi",
            "version": "v1",
        },
        "paths": path
    }
    try:
        OpenAPI(oapi)
        print("OpenAPI looks valid.")
    except SpecError as e:
        print("Validation error! {}".format(e.message))
        return

    if args.output:
        with open(args.output, "w") as o:
            yaml.dump(oapi, o, indent=2, Dumper=NoAliasDumper, sort_keys=False)
        print("Output written to {}".format(args.output))
    else:
        print("---")
        print(yaml.dump(oapi, indent=2, Dumper=NoAliasDumper, sort_keys=False))


if __name__ == '__main__':
    main()
