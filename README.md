# json2openapi

A simple python program to generate OpenApi documentation by supplying JSON request/response bodies.

## Motivation

Sometimes you have a fully functioning HTTP service without documentation.
At some point in time, others may need to use your service and they ask you to provide the OpenApi specification.
Writing the documentation by hand is a pain and can feel like an overwhelming job for complex services.
_json2openapi_ helps you generate your OpenApi specification by taking as input request/response examples plus some
other information.

The generated OpenApi specification is validated with [openapi3](https://github.com/Dorthu/openapi3).

_Warning_: This program also generates the `example` fields in OpenApi schemas by default.
If you have sensible data in your request/response files, disable this feature with `--no-example`

## Installation

Pipenv is used for dependencies. Create a virtual environment with:

```shell script
# clone repository
$ cd json2openapi
$ pipenv install 
```

## Usage

`json2openapi.py` provides its own help. Check it out with:

```shell script
$ pipenv run ./json2openapi.py --help
```

## Example

Let's consider a simple case: you have an HTTP service managing employees.
We want to generate OpenApi spec for a GET on all the employees, returning a 200 status code:

```shell script
$ pipenv run ./json2openapi.py GET /employees 200
```

<details><summary>output</summary>

```
OpenAPI looks valid.
---
openapi: 3.0.0
info:
  title: Generated by json2openapi
  version: v1
paths:
  /employees:
    get:
      responses:
        200:
          description: ''
          content: null
```

</details>

Now, a GET request with an empty response is not quite useful.
Let's add an argument with a JSON file containing a response example.
Input examples can be found in [examples](./examples).

```shell script
$ pipenv run ./json2openapi.py GET /employees 200 -respj ./examples/employees.json
```

<details><summary>output</summary>

```shell script
OpenAPI looks valid.
---
openapi: 3.0.0
info:
  title: Generated by json2openapi
  version: v1
paths:
  /employees:
    get:
      responses:
        200:
          description: ''
          content:
            application/json:
              schema:
                type: array
                items:
                  type: object
                  properties:
                    id:
                      type: integer
                      example: 1
                    name:
                      type: string
                      example: Dwight Schrute
                    role:
                      type: string
                      example: salesman
```

</details>

Finally, let's try a POST request with both request and response.

```shell script
$ pipenv run ./json2openapi.py POST /employees 201 -reqj ./examples/new_employee_req.json -respj ./examples/new_employee_resp.json
```

<details><summary>output</summary>

```shell script
OpenAPI looks valid.
---
openapi: 3.0.0
info:
  title: Generated by json2openapi
  version: v1
paths:
  /employees:
    post:
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
                  example: Michael Scott
                role:
                  type: string
                  example: manager
      responses:
        201:
          description: ''
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: integer
                    example: 4
                  name:
                    type: string
                    example: Michael Scott
                  role:
                    type: string
                    example: manager
```

</details>

If you want to directly write the generated OpenApi spec in a YAML file, just add `-o ./openapi.yaml`

## TODO list

- [ ] Add support for request/response files in YAML
- [ ] Add support for `application/yaml` content
- [ ] Add an integrated HTTP client to get responses from the service
- [ ] Add support for `headers`
- [ ] Add support for `links`
- [ ] Add support for `format`
