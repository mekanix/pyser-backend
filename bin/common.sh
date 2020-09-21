#!/bin/sh

export LC_ALL=C.UTF-8
export LANG=C.UTF-8
export BIN_DIR=`dirname $0`
export PROJECT_ROOT="${BIN_DIR}/.."
. "${PROJECT_ROOT}/name.py"
export VIRTUALENV=${VIRTUALENV:="${app_name}back"}
export FLASK_ENV=${FLASK_ENV:="production"}
export SYSPKG=${SYSPKG:="no"}

export PY_VERSION_MAJOR="3"
export PY_VERSION_MINOR="7"
export PY_VERSION=${PY_VERSION:="${PY_VERSION_MAJOR}.${PY_VERSION_MINOR}"}
export PY_VERSION_SHORT=${PY_VERSION_HORT:="${PY_VERSION_MAJOR}${PY_VERSION_MINOR}"}


setup() {
  cd "${PROJECT_ROOT}"
  if [ "${SYSPKG}" = "no" ]; then
    update=${1}
    if [ ! -d ${HOME}/.virtualenvs/${VIRTUALENV} ]; then
        python${PY_VERSION} -m venv "${HOME}/.virtualenvs/${VIRTUALENV}"
    fi
    . ${HOME}/.virtualenvs/${VIRTUALENV}/bin/activate

    cd ${PROJECT_ROOT}
    if [ "${update}" != "no" ]; then
      pip install -U pip
      pip install -U wheel
      pip install -U -r requirements.txt
    fi
  fi
}
