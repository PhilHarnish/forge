# ~/.bashrc: executed by bash(1) for non-login shells.
# see /usr/share/doc/bash/examples/startup-files (in the package bash-doc)
# for examples

# If not running interactively, don't do anything
[ -z "$PS1" ] && return

# don't put duplicate lines in the history. See bash(1) for more options
export HISTCONTROL=erasedups
export HISTSIZE=10000
shopt -s histappend

# Adds colors to ls
export CLICOLOR='true'
export LSCOLORS="gxfxcxdxbxegedabagacad"

export PATH="/usr/local/flex/bin:/usr/local/home/philharnish/bin:/usr/local/mysql/bin:$PATH"
export EDITOR="mate"

# check the window size after each command and, if necessary,
# update the values of LINES and COLUMNS.
shopt -s checkwinsize

# make less more friendly for non-text input files, see lesspipe(1)
[ -x /usr/bin/lesspipe ] && eval "$(lesspipe)"

# set variable identifying the chroot you work in (used in the prompt below)
if [ -z "$debian_chroot" ] && [ -r /etc/debian_chroot ]; then
    debian_chroot=$(cat /etc/debian_chroot)
fi

# Color prompt with git branch.
source ~/.git-completion.bash
export PS1='\e[32m\w\e[0m$(__git_ps1 "\e[34m(%s)\e[0m")$ '


# If this is an xterm set the title to user@host:dir
case "$TERM" in
xterm*|rxvt*)
    PROMPT_COMMAND='echo -ne "\033]0;${USER}@${HOSTNAME}: ${PWD/$HOME/~}\007"'
    ;;
*)
    ;;
esac

# enable color support of ls and also add handy aliases
if [ "$TERM" != "dumb" ] && [ -x /usr/bin/dircolors ]; then
    eval "`dircolors -b`"
    alias ls='ls --color=auto'
    alias dir='ls --color=auto --format=vertical'
    alias vdir='ls --color=auto --format=long'
fi

# some more ls aliases

alias ll='ls -l'
alias la='ls -A'
alias l='ls -CF'
alias cdl='cd /usr/local/home/philharnish/'
alias rhino='java org.mozilla.javascript.tools.shell.Main'

__project_comp() {
  COMPREPLY=()
  local cur="${COMP_WORDS[COMP_CWORD]}"
  local opts="`ls ~/Projects/`"
  COMPREPLY=($(compgen -W "${opts}" -- ${cur}))
}
project() {
  cd ~/Projects/$1
}
complete -F "__project_comp" -o "default" "project"

resource() {
  local rsrc="costanza.sbo.corp.google.com:/usr/local/google/home/philharnish/git/google3/flash/actionscript/com/google/youtube/resources/"
  local lsrc="./"
  local from=""
  local to=""
  case "$1" in
  get)
    from="$rsrc"
    to="$lsrc"
    ;;
  put)
    from="$lsrc"
    to="$rsrc"
    ;;
  *)
    return
    ;;
  esac
  scp $from/$2 $to/$2
}

test -r /sw/bin/init.sh && . /sw/bin/init.sh
