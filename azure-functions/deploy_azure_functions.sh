#!/bin/bash

# INPUTS

FUNCTION_APP=$1
RESOURCE_GROUP=$2
EVENTHUBS_NAMESPACE=$3
EVENTHUBS_TOPIC=$4
SQLDB_SERVER=$5
SQLDB_DBNAME=$6
SQLDB_ADMUSR=$7
SQLDB_PWD=$8
ORDER_DATA_GENERATOR_INTERVAL_MINUTES=$9

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

##########################################################
# FUNCTIONS E CONFIG
##########################################################

action="Setando variáveis de ambiente para as azure functions..."

echo $action

az functionapp config appsettings set \
--name $FUNCTION_APP \
--resource-group $RESOURCE_GROUP \
--settings \
EVENTHUBS_NAMESPACE=$EVENTHUBS_NAMESPACE \
EVENTHUBS_TOPIC=$EVENTHUBS_TOPIC \
SQLDB_SERVER=$SQLDB_SERVER \
SQLDB_DBNAME=$SQLDB_DBNAME \
SQLDB_ADMUSR=$SQLDB_ADMUSR \
SQLDB_PWD=$SQLDB_PWD \
ORDER_DATA_GENERATOR_INTERVAL_MINUTES=$ORDER_DATA_GENERATOR_INTERVAL_MINUTES

check_return "$action"


action="Publicando azure functions em '$FUNCTION_APP'..."

echo $action

func azure functionapp publish $FUNCTION_APP

check_return "$action"
