# docker-tools
Wrappers for simplified docker build and run

## Features

`dbuild` allows you to easily build your image with your host user inside. It resolves the permission problem - when you create files on volume as `root`, you should modify them on host as `root` as well. But having your own user inside the container solves this.

`drun` is just a wrapper for docker run, which adds `-it` and `--rm` flags by default.

## Installation

To install `docker-tools`, just run

    ./install

If you need to uninstall `docker-tools`, you can use

    ./uninstall

## Usage

Interfaces of `dbuild` and `drun` are the same as `docker build` and `docker run` respectively, so to build image you type

    dbuild . -t myimage

and it will build `myimage` and `username/myimage` with your user inside.

To run image, use

    drun [options] username/myimage

    drun [options] myimage

*NOTE: if you run `myimage`, you'll not have your user inside the container, but options `-it --rm` will still be present*
