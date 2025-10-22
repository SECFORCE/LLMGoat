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

This project is an open source, deliberately vulnerable environment created by <a href="https://www.secforce.com" target="_blank">SECFORCE</a> to learn about LLM-specific risks based on the <a href="https://genai.owasp.org/llm-top-10/" target="_blank">OWASP Top 10 for LLM Applications</a>.</p>

## ✨ Overview

***LLMGoat*** is a <b><u>vulnerable</u></b> environment with a collection of 10 challenges - one for each of the OWASP Top 10 for LLM Applications - where each challenge simulates a real-world vulnerability so you can easiliy learn, test and understand the risks associated with large language models.

This app could be useful to security professionals, developers who work with LLMs or anyone who is simply curious about LLM vulnerabilities. While some of the challenges require some knowledge of cybersecurity attacks, others only require clever use of natural language and some common sense.

You are encouraged to visit the link to the **OWASP Top 10** vulnerability included in each challenge description before attempting to solve the challenge, if you are unfamiliar with the vulnerability. Solutions to the challenges will be released in the coming months.

By default, ***LLMGoat*** will use the <a href="https://huggingface.co/bartowski/gemma-2-9b-it-GGUF" target="_blank">gemma-2 model</a> but you can try out other models by placing the corresponding `.gguf` file in the models folder (defaults to `$HOME/.LLMGoat/models`).

As the underlying model does not handle concurrent requests, the app is intended to be single-user.

Lastly and most importantly this is an <b><u>intentionally vulnerable</u></b> application and therefore you should never expose it to the Internet and ideally should run it in a fully segregated enviroment. We highly recommend you use *Docker* rather than running it directly on your own system. If you experiment with online models also keep in mind that these should be treated as untrusted too.

## 📋 Requirements

Minimum 8GB RAM for the default model. If you use larger model files YMMV.

For best performance, you should run ***LLMGoat*** on a system that has an NVIDIA GPU.

In this case, you will need to have:
- NVIDIA drivers
- CUDA and <a href="https://developer.nvidia.com/cuda-toolkit">CUDA toolkit</a> (we used version 12.2)

And if you use Docker (recommended):
- <a href="https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html">NVIDIA container toolkit</a> (might be necessary in some setups)
- Docker CE (as in Linux Docker might not see your GPU as explained <a href="https://forums.docker.com/t/cant-start-containers-with-gpu-access-on-linux-mint/144606">here</a>)

If you run it on a CPU-only system, then 10-12 cores at a minimum are recommended unless you are an extremely patient person.

## 📘 Usage

The *easiest* and *suggested* way of running ***LLMGoat*** is through Docker. We provide you with both pre-made Docker images and the Dockerfiles to build them on your own. If you want to use the GPU version, we recommend that you build the Docker image yourself so that it's optimised for your hardware/drivers.

### Run with `docker compose` (GitHub Docker Images)

Run the CPU version using the Docker image we publish on *GitHub*:

```sh
docker compose -f compose.github.yaml up llmgoat-cpu
```

Run the GPU version using the Docker image we publish on *GitHub*:

```sh
docker compose -f compose.github.yaml up llmgoat-gpu # If that doesn't work refer to the next section
```

### Run with `docker compose` (manual build)

For the following commands we assume you cloned the repo.

Run the CPU version by building it locally:

```sh
docker compose -f compose.local.yaml up llmgoat-cpu
```

Run the GPU version by building it locally:

```sh
# Build first
docker build --build-arg CUDA_ARCH=<value> -f Dockerfile.gpu -t llmgoat-gpu:latest .
# Then just run the service
docker compose -f compose.local.yaml up llmgoat-gpu
```

We **strongly** suggest that you set the `CUDA_ARCH` argument to speed up the build process. You can find the value for your GPU at [https://developer.nvidia.com/cuda-gpus](https://developer.nvidia.com/cuda-gpus). Bear in mind that the format of the `CUDA_ARCH` variable is **without dots**, meaning that if the *Compute Capatibility* is `10.3` you would have to specify it as `103`.

The GPU Dockerfile has been thorougly tested, but due to minor differences in your setup there may be issues while building or running the GPU version. In that case, if you cannot sort it out we suggest that you sacrifice performance and use the CPU version instead.

#### ENV variables

The compose files already contain default values that allow you to partially configure ***LLMGoat*** based on your specific setup:

| Variable                 | Description                                          | Default             |
| ------------------------ | ---------------------------------------------------- | ------------------- |
| `LLMGOAT_SERVER_HOST`    | Bind address                                         | `0.0.0.0`           |
| `LLMGOAT_SERVER_PORT`    | Bind port                                            | `5000`              |
| `LLMGOAT_DEFAULT_MODEL`  | Default model to use                                 | `gemma-2.gguf`      |
| `LLMGOAT_N_THREADS`      | Number of threads LLama can use                      | `16`                |
| `LLMGOAT_N_GPU_LAYERS`   | Number of GPU layers to use (0 to disable it)        | `0 (cpu), 20 (gpu)` |
| `LLMGOAT_VERBOSE`        | Enable verbose mode (1 for verbose, 0 for silent)    | `0`                 |
| `LLMGOAT_DEBUG`          | Enable debug mode (1 for verbose, 0 for silent)      | `0`                 |

### Run locally

| :exclamation: **Disclaimer** |
| ---------------------------- |
| **Even if we made it possible to install LLMGoat locally, we strongly discourage you to use it this way. Since this is an intentionally vulnerable application it may harm your system if it has access to it.** |

#### CPU

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

#### GPU
It is difficult to provide build instructions for every OS so we recommend that you refer to the official <a href="https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md#cuda">llama-cpp</a> / <a href="https://github.com/abetlen/llama-cpp-python/">llama-cpp-python</a> repos as the key challenge you might face is trying to compile llama-cpp with GPU support.

On an Ubuntu base system, this is what worked for us:

- Follow the instructions for the CPU version to install the requirements
- Install CUDA
```sh
sudo wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update

# install the runtime (pick one that matches your driver: 12.2 or 12.1 are safe bets)
sudo apt-get -y install cuda-runtime-12-2
```
- Reinstall torch to avoid version incompatibility
```sh
pip uninstall -y torch torchvision torchaudio
pip install --index-url https://download.pytorch.org/whl/cpu torch torchvision torchaudio
```
- Install CUDA toolkit and add paths
```sh
sudo apt-get install -y cuda-toolkit-12-2
export PATH=/usr/local/cuda-12.2/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-12.2/lib64:$LD_LIBRARY_PATH
source ~/.bashrc
```
- Reinstall llama-cpp-python with GPU support
```sh
pip uninstall llama-cpp-python
CMAKE_ARGS="-DGGML_CUDA=on" FORCE_CMAKE=1 pip install llama-cpp-python --no-cache-dir -vvvvv
```
- Launch the app as explained in the CPU section but set the gpu layers argument (e.g. `-g 20`) to make sure the GPU is used

#### CLI Options

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

╭─ Options ───────────────────────────────────────────────────────────────────────────────╮
│ --host        -h    TEXT     Host for API server (e.g. '0.0.0.0') [default: 127.0.0.1]  │
│ --port        -p    INTEGER  Port for API server [default: 5000]                        │
│ --model       -m    TEXT     The default model to use [default: gemma-2]                │
│ --threads     -t    INTEGER  Number of LLM threads [default: 16]                        │
│ --gpu-layers  -g    INTEGER  Number of GPU layers to use [default: 0 (no GPU)]          │
│ --verbose     -v             Display verbose output                                     │
│ --debug       -d             Enable debug mode and get prompts                          │
│ --help                       Show this message and exit                                 │
╰─────────────────────────────────────────────────────────────────────────────────────────╯

```

## 🪪 License

_LLMGoat_ is released under the [GPL-3.0 LICENSE](./LICENSE)

## 📚 Credits

Developed by [@SECFORCE](https://www.secforce.com).

Created by [Antonio Quina](https://x.com/st3r30byt3), with major contributions from [Rodrigo Fonseca](https://github.com/rlmd-fonseca) and [Angelo Delicato](https://github.com/thelicato).