#!/bin/bash

# FONTE: https://learn.microsoft.com/en-us/azure/data-factory/quickstart-create-data-factory-azure-cli

# INPUTS

RESOURCE_GROUP=$1
DATA_FACTORY=$2

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


action="Criando linked service 'ls_stockquotes'..."

echo $action

az datafactory linked-service create \
--resource-group $RESOURCE_GROUP \
--factory-name $DATA_FACTORY \
--linked-service-name ls_stockquotes \
--properties linkedService/ls_stockquotes.json

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


action="Criando linked service 'ls_datalake_storage'..."

echo $action

az datafactory linked-service create \
--resource-group $RESOURCE_GROUP \
--factory-name $DATA_FACTORY \
--linked-service-name ls_datalake_storage \
--properties linkedService/ls_datalake_storage.json

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


action="Criando dataset 'ds_datalake_storage'..."

echo $action

az datafactory dataset create \
--resource-group $RESOURCE_GROUP \
--dataset-name ds_datalake_storage \
--factory-name $DATA_FACTORY \
--properties dataset/ds_datalake_storage.json

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


action="Criando dataset 'ds_stockquotes'..."

echo $action

az datafactory dataset create \
--resource-group $RESOURCE_GROUP \
--dataset-name ds_stockquotes \
--factory-name $DATA_FACTORY \
--properties dataset/ds_stockquotes.json

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


action="Criando pipeline 'pipeline_stockquotes'..."

echo $action

az datafactory pipeline create \
--resource-group $RESOURCE_GROUP \
--factory-name $DATA_FACTORY \
--name pipeline_stockquotes \
--pipeline pipeline/pipeline_stockquotes.json

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"
