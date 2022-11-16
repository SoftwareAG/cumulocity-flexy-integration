# cumulocity-flexy-integration
------------------------------

These tools are provided as-is and without warranty or support. They do not constitute part of the Software AG product suite. Users are free to use, fork and modify them, subject to the license agreement. While Software AG welcomes contributions, we cannot guarantee to include every contribution in the master project.

## Repository Purpose and How to Get Startet

This repository provides documentation about the HMS Ewon Flex integration into Cumulocity IoT offered by Software AG.  The tool can be used within the certification tenant that will be provided during the technical onboarding process. 

The files [Endpoints](./docs/endpoints.md)  provide inside information on the tool. Interested readers can consume this information to get a deeper understanding of the tool itself.

[Quickstart Guide](./docs/quick-start-guide.md)

## Documentation Overview

[Documentation ](./docs/README.md)

## Getting started

1. Clone the project

    ```sh
    git clone https://github.com/SoftwareAG/cumulocity-flexy-integration.git
    ```

2. Edit the `.env` file to match the target Cumulocity instance

3. Press F5 (or debug) to start the microservice locally

## Sending manual API calls

`go-c8y-cli` is installed in the dev container, and a few convenience aliases have been set in bash and zsh to make it easy to send API calls against the microservice.

The calls need to be sent from inside VSCode 

1. Open a bash or zsh terminal (within the dev container (i.e. in VS Code)). The `.env` file (containing your c8y credentials) is automatically imported to the shell session.

### Locally hosted microservice

1. Make sure the microservice (flask app) is running in VS Code (either via debug or using `invoke start-production-local`)

    ```bash
    # Check health endpoint
    msapi GET /health

    # Change the log level of the app in runtime
    msapi POST /loglevel --data "level=DEBUG"
    ```

**Note:**

The `msapi` is just a shell alias for `c8y api --host http://127.0.0.1:5000`. The `--host` flag is used to redirect the API call to the locally running microservice.

### Hosted in Cumulocity

When the microservice is running in Cumulocity then the REST requests can be sent using:

```bash
# Check health endpoint
c8y api GET /health

# Change the log level of the app in runtime
c8y api POST /loglevel --data "level=DEBUG"
```

## Project tasks

The project is setup to use [invoke](http://www.pyinvoke.org/) to run tasks such as build, deploy etc.

The list of tasks and descriptions can be views using the following command: 

```sh
invoke --list
```

Invoke also has the tab completion enabled in both bash and zsh, so you can discover the available commands by using:

```sh
invoke <TAB><TAB>
```

### Linting

pylint is used to ensure consistency within the python source files and can be run using:

```sh
invoke lint
```

### Build

The microservice can be built using:

```sh
invoke build
```

The build step will build the python project (injecting a version number based on the current tag), then build a Cumulocity microservice zip file based on a production Dockerfile.

### Test

Tests are run via `pytest` and can be executed using:

```sh
invoke test
```

The tests are defined under the `./tests` folder.

## Deploy

If you want to deploy it to the configured Cumulocity instance (as defined in the `.env` file), then run:

```sh
# If you have already previously run build
invoke deploy

# If you want to build then deploy in one step (skipping lint and test) - FOR DEV ONLY!
invoke build deploy

# Deploying (with linting and testing!) - RECOMMENDED for PRODUCTION
invoke lint build test deploy
```
