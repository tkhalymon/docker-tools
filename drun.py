#!/usr/bin/env python
import argparse
import getpass
import re
import os


def fullTag(tag):
    """
    Args:
        tag: string in format '[<user>/]<tag>[:<version>]'

    Returns:
        string in format '<user>/<tag>:<version>'

    Raises:
        ValueError
    """
    match = re.match(r"^(?:([\w]{0,64})\/)?([\w][\w.-]{0,64})"
                     r"(?::([\w.-]{1,32}))?$", args.tag)
    if not match:
        raise NameError("'{0}' is not a valid image tag, should be "
                        "'[<user>/]<name>[:<version>]'".format(args.tag))
    user, tag, version = match.groups()
    user = user or getpass.getuser()
    version = version or "latest"
    return "{0}/{1}:{2}".format(user, tag, version)


def getMounts(mounts):
    """
    Args:
        mounts: list of strings in format `<source path>:<target path>[:ro]`

    Returns:
        list of strings in format:
        ["--mount", "type=bind,source=<source path>,target=<target path>", ...]
    Raises:
        SyntaxError, ValueError, IOError
    """
    if not mounts:
        return []
    result = []
    for mount in mounts:
        # <any character except :>:<any character except :>[:ro]
        match = re.match(r"^([^:]+):([^:]+)(:?ro)?$", mount)
        if not match:
            raise SyntaxError("Mount: '{0}' - should be '<source path>"
                              ":<target path>[:ro]'".format(mount))
        else:
            source, target, readonly = match.groups()
            readonly = "true" if readonly else "false"
            if not os.path.isdir(source):
                raise IOError("Mount: source path '{0}' "
                              "is not a directory".format(source))
            else:
                source = os.path.abspath(source)
            if not os.path.isabs(target):
                raise ValueError("Mount: target path '{0}' "
                                 "should be absolute".format(target))
            result.append("--mount")
            result.append("type=bind,src={0},dst={1},ro={2}"
                          "".format(source, target, readonly))
    return result


def getPorts(ports):
    """
    Args:
        ports: list of strings in format `<port>` or `<port>:<internal port>`

    Returns:
        list of strings in format:
        ["-p", "<port>:<internal port>", ...]
        if internal port not specified it is replaced by `<port>`
    Raises:
        SyntaxError, ValueError
    """
    if not ports:
        return []
    result = []
    for port in args.port:
        # <1-5 digits>[:1-5 digits]
        match = re.match(r"^([0-9]{1,5})(?::([0-9]{1,5}))?$", port)
        port_exception = "Port: '{0}' should be '<port>' or '<port>:"\
                         "<internal port>'. Ports should be numbers "\
                         "in [1-65535]".format(port)
        if not match:
            raise SyntaxError(port_exception)
        else:
            public, internal = match.groups()
            # if internal port is not set, using public
            internal = internal or public
            # check if port is in Unix limit
            if int(public) > 65535 or int(internal) > 65535:
                raise ValueError(port_exception)
            result.extend(["-p", "{0}:{1}".format(public, internal)])
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run docker image")
    parser.add_argument("tag", type=str, help="Docker image tag [<user>/]<tag>[:<version>]")
    parser.add_argument("-g", "--gpu", type=str,
                        help="Visible GPU devices - comma-"
                        "separated GPU IDs: '0', '0,1', etc.")
    parser.add_argument("-m", "--mount", type=str, action="append",
                        help="Mount directories '<source>:<target>[:ro]'. "
                        "'ro' - for mounting in read-only mode")
    parser.add_argument("-p", "--port", type=str, action="append",
                        help="Forwarded ports '<port>' or '<port>:<internal port>'")
    parser.add_argument("--root", action='store_true',
                        help="Build image with root user")
    parser.add_argument("cmd", type=str, nargs="?", action="append", default=None,
                        help="Command to be executed in container")
    args = parser.parse_args()

    command = []
    if args.gpu:
        # 1-10 numbers in [0, 9]
        if re.match(r"^(?:[0-9],){0,9}[0-9]$", args.gpu):
            # set environment variable NV_GPU to declare visible devices
            os.putenv("NV_GPU", args.gpu)
            command.append("nvidia-docker")
        else:
            raise ValueError("Invalid GPU options: '{0}', should be comma-"
                             "separated GPU IDs: '0', '0,1', ...".format(args.gpu))
    else:
        # if no GPUs required, using docker - for machines without nvidia-docker
        command.append("docker")

    command.extend(["run", "-it", "--rm"])
    if not args.root:
        command.extend(["--user", "{0}:{1}".format(os.getuid(), os.getgid())])
    command.extend(getMounts(args.mount))
    command.extend(getPorts(args.port))

    imageTag = fullTag(args.tag)
    command.append(imageTag)
    if args.cmd[0]:
        command.extend(args.cmd)
    else:
        command.append("bash")
    # run command (docker/nvidia-docker) and pass arguments (including command itself)
    os.execvp(command[0], command)
