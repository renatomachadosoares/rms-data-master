#!/bin/bash

# INPUTS

FUNCTION_APP=$1

#########################################################
# AUX FUNCTIONS
#########################################################

check_return() {

    ret=$?

    action=$1

    if [ $ret -ne 0 ]; then
        echo "Erro ao executar a ação: '$1'"
        exit 1
    fi

}


action="Publicando azure functions em '$FUNCTION_APP'..."

echo $action

#cd azure-functions

func azure functionapp publish $FUNCTION_APP

check_return "$action"

#cd -