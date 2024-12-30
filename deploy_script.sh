#!/bin/bash

#########################################################
# RESOURCES NAMES
#########################################################

LOCATION="Brazil South"
RESOURCE_GROUP="rsgrmsdms810401"
STORAGE_ACCOUNT="starmsdms810401"
DATA_FACTORY="dtfrmsdms810401"
FUNCTION_APP="afarmsdms810401"


#########################################################
# FUNCTIONS
#########################################################

check_return() {

    ret=$?

    action=$1

    if [ $ret -ne 0 ]; then
        echo "Erro ao executar a ação: '$1'"
        exit 1
    fi

}

#########################################################
# AZURE CLI CONFIGS
#########################################################

az config set extension.use_dynamic_install=yes_without_prompt


#########################################################
# Instanciando os recursos
#########################################################

# RESOURCE GROUP

action="Criando resource group '$RESOURCE_GROUP'..."

echo $action

az group create \
--name $RESOURCE_GROUP \
--location "$LOCATION"

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


# STORAGE ACCOUNT

action="Criando storage account '$STORAGE_ACCOUNT'..."

echo $action

az storage account create \
--name $STORAGE_ACCOUNT \
--location "$LOCATION" \
--resource-group $RESOURCE_GROUP \
--sku Standard_LRS

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


# DATA FACTORY

action="Criando data factory '$DATA_FACTORY'..."

echo $action

az datafactory create \
--resource-group $RESOURCE_GROUP \
--name $DATA_FACTORY \
--location "$LOCATION"

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


# AZURE FUNCTION APP

action="Criando azure function app '$FUNCTION_APP'..."

echo $action

az functionapp create \
--resource-group $RESOURCE_GROUP \
--consumption-plan-location brazilsouth \
--runtime python \
--runtime-version 3.11 \
--functions-version 4 \
--name $FUNCTION_APP \
--os-type linux \
--storage-account $STORAGE_ACCOUNT

check_return "$action"

echo "Aguardando efetivação da criação do recurso..."
sleep 15    # Dorme alguns segundos para garantir que a publicação das functions não falhe

echo "-----------------------------------------------------------------------------------------------------------------------"



#########################################################
# Publicando os recursos
#########################################################

action="Publicando as azure functions..."

echo $action

cd azure-functions

func azure functionapp publish $FUNCTION_APP

check_return "$action"

cd -

pwd
