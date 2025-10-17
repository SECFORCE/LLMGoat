<h1 align="center">
  <br>
    <img src="./logo.png" alt= "LLMGoat" width="400px">
</h1>
<p align="center">
    <b>LLMGoat</b>
<p>

<p align="center">
    <a href="./README.md"><img src="https://img.shields.io/badge/Documentation-complete-green.svg?style=flat"></a>
    <a href="./LICENSE"><img src="https://img.shields.io/badge/License-GPL3-blue.svg"></a>
</p>

This project is a deliberately vulnerable environment to learn about LLM-specific risks based on the OWASP Top 10 for LLM Applications.

## ✨ Overview

WIP

## 📋 Requirements

WIP

## 📘 Usage

The *easiest* and *suggested* way of running ***LLMGoat*** is through Docker. We provide you both pre-made Docker images and the Dockerfiles to build it on your own. The normal Docker images (and the default `Dockerfile`) can be used in case you don't have/need a GPU. If you want to use the GPU version you should build the Docker image locally.

### Run with `docker compose` (GitHub Docker Images)

Run the CPU version using the Docker image we publish on *GitHub*:

```sh
docker compose -f github.yaml up llmgoat-cpu
```

Run the GPU version using the Docker image we publish on *GitHub*:

```sh
docker compose -f github.yaml up llmgoat-gpu # If that doesn't work refer to the next section
```

### Run with `docker compose` (manual build)

For the following commands we assume you cloned the repo.

Run the CPU version by building it locally:

```sh
docker compose -f local.yaml up llmgoat-cpu
```

Run the GPU version by building it locally:

```sh
# Build first
docker build --build-arg CUDA_ARCH=<value> -f Dockerfile.gpu -t llmgoat-gpu:latest .
# Then just run the service
docker compose -f local.yaml up llmgoat-gpu
```

We **strongly** suggest you to set the `CUDA_ARCH` to speed up the build process. You can find the value for your GPU at [https://developer.nvidia.com/cuda-gpus](https://developer.nvidia.com/cuda-gpus). Bear in mind that the format of the `CUDA_ARCH` variable is **without dots**, meaning that if the *Compute Capatibility* is `10.3` you would have to specify it as `103`.

The GPU Dockerfile has been thorougly tested, but due to minor differences in your setup there may be issues while building or running the GPU version. In that case, we suggest you to sacrifice performances and use the CPU version instead.

### ENV variables

The compose files already contain default values that allow you to partially configure ***LLMGoat*** based on your specific setup:

| Variable                 | Description                                          | Default        |
| ------------------------ | ---------------------------------------------------- | -------------- |
| `LLMGOAT_SERVER_HOST`    | Bind address                                         | `0.0.0.0`      |
| `LLMGOAT_SERVER_PORT`    | Bind port                                            | `5000`         |
| `LLMGOAT_DEFAULT_MODEL`  | Default model to use                                 | `gemma-2.gguf` |
| `LLMGOAT_N_THREADS`      | Number of threads LLama can use                      | `16`           |
| `LLMGOAT_N_GPU_LAYERS`   | Number of GPU layers to use (0 to disable it)        | `0`            |
| `LLMGOAT_VERBOSE`        | Enable verbose mode (1 for verbose, 0 for silent)    | `0`            |

## Run locally

| :exclamation: **Disclaimer**                                                                                  |
| ------------------------------------------------------------------------------------------------------------- |
| **Even if we made it possible to install LLMGOAT locally, we strongly discourage you to use it this way.** |
| **Since this is an intentionally vulnerable application it may harm your system if it has access to it.**  |

If you want to run it locally you can install it in the following ways.

Clone, install, run

```sh
# Clone
git clone https://github.com/SECFORCE/LLMGoat
cd LLMGoat
# Install
pipx install . # pipx is (always) suggested
# Run
llmgoat
```

Install it directly

```sh
# Install it
pipx install git+https://github.com/SECFORCE/LLMGoat
# Run
llmgoat
```

### Options

The CLI allows you to obtain the same level of customisation as the ENV variables:

```
llmgoat --help

      ░█░░░█░░░█▄█
      ░█░░░█░░░█░█
      ░▀▀▀░▀▀▀░▀░▀
    ░█▀▀░█▀█░█▀█░▀█▀
    ░█░█░█░█░█▀█░░█░
    ░▀▀▀░▀▀▀░▀░▀░░▀░
    LLMGoat v0.1.0


 Usage: llmgoat [OPTIONS]

 Start LLMGoat

╭─ Options ───────────────────────────────────────────────────────────────────────────────────────╮
│ --host         -h        TEXT     Host for API server (e.g. '0.0.0.0') [default: 127.0.0.1]     │
│ --port         -p        INTEGER  Port for API server [default: 5000]                           │
│ --model        -m        TEXT     The default model to use [default: gemma-2]                   │
│ --threads      -t        INTEGER  Number of LLM threads [default: 16]                           │
│ --gpu-layers   -g        INTEGER  Number of GPU layers to use [default: 0 (no GPU)]             │
│ --verbose      -v                 Display verbose output                                        │
│ --help                            Show this message and exit                                    │
╰─────────────────────────────────────────────────────────────────────────────────────────────────╯

```

## 🪪 License

_LLMGoat_ is released under the [GPL-3.0 LICENSE](./LICENSE)