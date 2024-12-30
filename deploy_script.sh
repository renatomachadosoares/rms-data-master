#!/bin/bash

#########################################################
# Pré-requisito para execução:
#
# Login na Azure através do comando abaixo:
#
# az login --tenant <TENANT-ID>
#########################################################


#########################################################
# AZURE CONSTANTS
#########################################################

SUBSCRIPTION_ID="8071356f-927f-41b5-a491-71b837d0d882"
LOCATION="Brazil South"
RESOURCE_GROUP="rsgrmsdms810401"
STORAGE_ACCOUNT="starmsdms810401"
CONTAINER_LAKE="ctnlake"
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
# AZURE CLI CONFIG
#########################################################

az config set extension.use_dynamic_install=yes_without_prompt


#########################################################
# Instanciando os recursos
#########################################################


# ***************************************************************************************************************************
# RESOURCE GROUP
# ***************************************************************************************************************************

action="Criando resource group '$RESOURCE_GROUP'..."

echo $action

az group create \
--name $RESOURCE_GROUP \
--location "$LOCATION"

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"

sleep 10


# ***************************************************************************************************************************
# STORAGE ACCOUNT
# ***************************************************************************************************************************

action="Criando storage account '$STORAGE_ACCOUNT'..."

echo $action

az storage account create \
--name $STORAGE_ACCOUNT \
--resource-group $RESOURCE_GROUP \
--location "$LOCATION" \
--sku Standard_LRS \
--kind StorageV2 \
--hierarchical-namespace true

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"

sleep 20


# ***************************************************************************************************************************
# CONTAINER DO DATA LAKE
# ***************************************************************************************************************************

action="Criando container do lake '$CONTAINER_LAKE'..."

echo $action

az storage container create \
--name $CONTAINER_LAKE \
--account-name $STORAGE_ACCOUNT \
--auth-mode login

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"

sleep 30


# ***************************************************************************************************************************
# DIRETORIOS DO CONTAINER LAKE
# ***************************************************************************************************************************

action="Criando diretório 'raw' no container do lake '$CONTAINER_LAKE'..."

echo $action

az storage fs directory create -n "raw" -f $CONTAINER_LAKE --account-name $STORAGE_ACCOUNT --auth-mode login

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


action="Criando diretório 'bronze' no container do lake '$CONTAINER_LAKE'..."

echo $action

az storage fs directory create -n "bronze" -f $CONTAINER_LAKE --account-name $STORAGE_ACCOUNT --auth-mode login

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


action="Criando diretório 'silver' no container do lake '$CONTAINER_LAKE'..."

echo $action

az storage fs directory create -n "silver" -f $CONTAINER_LAKE --account-name $STORAGE_ACCOUNT --auth-mode login

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


action="Criando diretório 'gold' no container do lake '$CONTAINER_LAKE'..."

echo $action

az storage fs directory create -n "gold" -f $CONTAINER_LAKE --account-name $STORAGE_ACCOUNT --auth-mode login

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


# ***************************************************************************************************************************
# DATA FACTORY
# ***************************************************************************************************************************

action="Criando data factory '$DATA_FACTORY'..."

echo $action

az datafactory create \
--resource-group $RESOURCE_GROUP \
--name $DATA_FACTORY \
--location "$LOCATION"

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"

sleep 30


# ***************************************************************************************************************************
# MANAGED IDENTITY DATA FACTORY 
# ***************************************************************************************************************************

action="Obtendo a managed identity do data factory..."

echo $action

mng_ident_id_dtf=$(grep -oP '(?<="principalId": ")[^"]*' <<< $(az datafactory show --resource-group $RESOURCE_GROUP --name $DATA_FACTORY))

check_return "$action"

echo $mng_ident_id_dtf

echo "-----------------------------------------------------------------------------------------------------------------------"


# ***************************************************************************************************************************
# ROLE DATA CONTRIBUTOR NO STORAGE ACCOUNT PARA O DATA FACTORY
# ***************************************************************************************************************************

# Atribuindo a role de 'storage blob data contributor' para a system managed identity do Data Factory no Storage account. 

action="Setando role 'data crontributor' para o data factory no storage account..."

echo $action

az role assignment create \
--assignee $mng_ident_id_dtf \
--role 'Storage Blob Data Contributor' \
--scope subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACCOUNT

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


# ***************************************************************************************************************************
# AZURE FUNCTION APP
# ***************************************************************************************************************************

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
