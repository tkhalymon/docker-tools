#!/usr/bin/env bash
source /usr/share/bash-completion/completions/docker

function _docker_tools_build() {
    COMP_WORDS_BAK=${COMP_WORDS[@]}
    COMP_CWORD_BAK=$COMP_CWORD
    COMP_LINE=${COMP_LINE/dbuild/docker build}
    COMP_WORDS=(${COMP_WORDS[@]/dbuild/docker build})
    COMP_CWORD=$((COMP_CWORD + 1))
    COMP_POINT=$((COMP_POINT + 6))
    _docker
}

function _docker_tools_run() {
    COMP_WORDS_BAK=${COMP_WORDS[@]}
    COMP_CWORD_BAK=$COMP_CWORD
    COMP_LINE=${COMP_LINE/drun/docker run}
    COMP_WORDS=(${COMP_WORDS[@]/drun/docker run})
    COMP_CWORD=$((COMP_CWORD + 1))
    COMP_POINT=$((COMP_POINT + 6))
    _docker
}

complete -F _docker_tools_build dbuild
complete -F _docker_tools_run drun
