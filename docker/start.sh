#!/bin/bash

function run_ssh_server() {
    mkdir -p /root/.ssh
    echo "$SSH_PUBLIC_KEY" >> /root/.ssh/authorized_keys
    chmod 0600 /root/.ssh/authorized_keys
    mkdir -p -m 0755 /var/run/sshd
    /usr/sbin/sshd -e
}

function run_user_custom_command() {
    if [ ! -z "$TRAIN_TRIGGER_COMMAND" ]
    then
        exec $TRAIN_TRIGGER_COMMAND
    fi
} 

function run_jupyter_notebook() {
    sed -i "s/^c.NotebookApp.token.*$/c.NotebookApp.token = '$JUPYTER_TOKEN'/g"   /root/.jupyter/jupyter_notebook_config.py
    sed -i "s/#c.NotebookApp.base_url.*$/c.NotebookApp.base_url = '${TASK_NAME}\/'/g"   /root/.jupyter/jupyter_notebook_config.py
    exec jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root
}

function run_tensorflow_session() {
    if [ $TRAIN_WIPE_ENGINE_DATA -eq "1" ]
    then
        rm -rf $MODEL_PATH/*
    fi

    run_ssh_server

    case $TRAIN_TRIGGER_METHOD in
        "default") run_jupyter_notebook ;;
        "custom") run_user_custom_command ;;
    esac
}

case $RESOURCE_TYPE in
    "session"     ) run_tensorflow_session ;;
esac


