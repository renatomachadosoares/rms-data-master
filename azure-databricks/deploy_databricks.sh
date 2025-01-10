#!/bin/bash

# INPUTS

SUBSCRIPTION_ID=$1
RESOURCE_GROUP=$2
DATABRICKS=$3
STORAGE_ACCOUNT=$4
CONTAINER_LAKE=$5
LOCATION=$6
DATABRICKS_ACCESS_CONECTOR=$7
DATABRICKS_UNITY_CATALOG_NAME=$8
DATABRICKS_WORKSPACE_PROJECT_DIR=$9


# CONSTANTES

UNITY_CREDENTIAL_NAME="unity-credential"


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


# Criando o workspace

action="Criando o workspace databricks '$DATABRICKS'..."

echo $action

az databricks workspace create \
--resource-group $RESOURCE_GROUP \
--name $DATABRICKS \
--location "$LOCATION" \
--sku premium

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"

sleep 20

# Criando o conector de acesso

action="Criando o conector de acesso '$DATABRICKS_ACCESS_CONECTOR' para o databricks '$DATABRICKS'..."

echo $action

az databricks access-connector create \
--resource-group $RESOURCE_GROUP \
--name $DATABRICKS_ACCESS_CONECTOR \
--location "$LOCATION" \
--identity-type SystemAssigned

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"

sleep 10

# Obtendo o system managed Id do conector de acesso do databricks

action="Obtendo o system managed Id do conector de acesso do databricks..."

echo $action

mng_ident_id_adb=$(grep -oP '(?<="principalId": ")[^"]*' <<< $(az databricks access-connector show --resource-group $RESOURCE_GROUP --name $DATABRICKS_ACCESS_CONECTOR))

check_return "$action"

echo $mng_ident_id_adb

echo "-----------------------------------------------------------------------------------------------------------------------"


# Atribuindo role data contributor no storage account para o conector de acesso do databricks

action="Setando role 'Storage Blob Data Contributor' no storage account para o databricks..."

echo $action

az role assignment create \
--assignee $mng_ident_id_adb \
--role 'Storage Blob Data Contributor' \
--scope subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACCOUNT

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


# Atribuindo role storage queue data contributor no storage account para o conector de acesso do databricks

action="Setando role 'Storage Queue Data Contributor' no storage account para o databricks..."

echo $action

az role assignment create \
--assignee $mng_ident_id_adb \
--role 'Storage Queue Data Contributor' \
--scope subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACCOUNT

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


# Atribuindo role event grid contributor no storage account para o conector de acesso do databricks

action="Setando role 'EventGrid EventSubscription Contributor' no storage account para o databricks..."

echo $action

az role assignment create \
--assignee $mng_ident_id_adb \
--role 'EventGrid EventSubscription Contributor' \
--scope subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACCOUNT

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


# Obtem info do workspace criado

action="Obtendo metadados do workspace databricks..."

echo $action

databricks_metainfo=$(az resource show -g $RESOURCE_GROUP --resource-type Microsoft.Databricks/workspaces -n $DATABRICKS)

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


# Obtem URL e Id do workspace a partir da info do workspace

action="Obtendo URL e ID do workspace databricks a partir dos metadados..."

echo $action

db_host_location=$(grep -oP '(?<="workspaceUrl": ")[^"]*' <<< $databricks_metainfo)

ws_id=$(grep -oP '(?<="workspaceId": ")[^"]*' <<< $databricks_metainfo)
ws_url="https://$db_host_location"

echo "Workspace ID: $ws_id"
echo "Workspace URL: $ws_url"

echo "-----------------------------------------------------------------------------------------------------------------------"


# Obtem o token bearer de autorização (OAuth 2.0) para acesso ao workspace Databricks

action="Obtendo token de acesso ao workspace databricks..."

echo $action

# IMPORTANTE: O resource ID usado no comando é fixo para o Databricks na Azure, não mudar!!!!

token=$(grep -oP '(?<="accessToken": ")[^"]*' <<< $(az account get-access-token --resource 2ff814a6-3304-4ab8-85cb-cd0e6f879c1d))

check_return "$action"

echo $token

echo "-----------------------------------------------------------------------------------------------------------------------"


# Criar o PAT (Personal Access Token) através da api rest do Databricks

action="Criando Personal Access Token para o Databricks..."

echo $action

api_response=$(curl -k -X POST $ws_url/api/2.0/token/create \
-H "Authorization: Bearer $token" \
-H "Content-Type: application/json" \
-d '{ "lifetime_seconds": 14400, "comment": "Token de acesso case Data Master" }')

check_return "$action"

pat_token=$(grep -oP '(?<="token_value": ")[^"]*' <<< $api_response)

echo $pat_token

echo "-----------------------------------------------------------------------------------------------------------------------"


# Exportar as variáveis de ambiente necessárias para uso do databrics CLI 

# NOTA: Para que o databricks CLI possa ser utilizado é preciso exportar as variáveis abaixo

action="Exportando variáveis de ambiente necessárias para uso do Databricks CLI..."

echo $action

export DATABRICKS_HOST=$ws_url 

export DATABRICKS_TOKEN=$pat_token 

echo "-----------------------------------------------------------------------------------------------------------------------"


# Habilitando o Unity: passo 1 - Verificando se existe um metastore (só pode existir um na região), se não existir cria.

action="Verificando se já existe um metastore Unity..."

echo $action

metastore_id=$(grep -oP '(?<="metastore_id": ")[^"]*' <<< $(databricks metastores list -o json))

if [ "$metastore_id" = "" ];then

    action="Nenhum metastore encontrado. Criando metastore..."

    echo $action

    databricks metastores create "metastore" --storage-root "abfss://$CONTAINER_LAKE@$STORAGE_ACCOUNT.dfs.core.windows.net/metastore" --region "brazilsouth" 

    check_return "$action"

    metastore_id=$(grep -oP '(?<="metastore_id": ")[^"]*' <<< $(databricks metastores list -o json))

fi

echo "ID do metastore: $metastore_id"

echo "-----------------------------------------------------------------------------------------------------------------------"

sleep 10


# Habilitando o Unity: passo 2 - Associar o workspace ao metastore

action="Associando workspace ao metastore Unity..."

echo $action

databricks metastores assign $ws_id $metastore_id "$DATABRICKS_UNITY_CATALOG_NAME"

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


# Habilitando o Unity: passo 3 - Criando as credenciais do storage para acesso através do Unity

# Referencias: 
# https://learn.microsoft.com/en-us/azure/databricks/data-governance/unity-catalog/azure-managed-identities
# https://learn.microsoft.com/en-us/azure/databricks/data-governance/unity-catalog/azure-managed-identities#upgrade-metastore

action="Criando credencial de acesso para o Unity no storage account a partir do conector de acesso Databricks..."

echo $action

st_cred_ret=$(databricks storage-credentials create --json '{
  "name": "'$UNITY_CREDENTIAL_NAME'",
  "azure_managed_identity": {
    "access_connector_id": "/subscriptions/'$SUBSCRIPTION_ID'/resourceGroups/'$RESOURCE_GROUP'/providers/Microsoft.Databricks/accessConnectors/'$DATABRICKS_ACCESS_CONECTOR'"
  }
}')

check_return "$action"

id_st_cred=$(grep -oP '(?<="id": ")[^"]*' <<< $(databricks storage-credentials list -o json))

echo "Id da credencial criada: $id_st_cred"

echo "-----------------------------------------------------------------------------------------------------------------------"

sleep 5


# Habilitando o Unity: passo 4 - Atualizando o metastore com a credencial de acesso necessária para acessar o storage

action="Atualizando metastore com credencial de acesso ao storage..."

echo $action

databricks metastores update $metastore_id --storage-root-credential-id $id_st_cred

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


# Habilitando o Unity: passo 5 - Criando o catálogo

# Verificando se o catálogo existe

action="Verificando se o catálogo '$DATABRICKS_UNITY_CATALOG_NAME' existe..."

echo $action

databricks catalogs get $DATABRICKS_UNITY_CATALOG_NAME

ret=$?

if [ $ret -ne 0 ]; then

    action="O catálogo não existe, criando..."

    echo $action

    databricks catalogs create "$DATABRICKS_UNITY_CATALOG_NAME"

    check_return "$action"

fi

echo "-----------------------------------------------------------------------------------------------------------------------"


# Criando um diretório no workspace

action="Criando diretório no workspace..."

echo $action

databricks workspace mkdirs "$DATABRICKS_WORKSPACE_PROJECT_DIR"

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


# Importando os notebooks do projeto para o workspace databricks

action="Importando os notebooks..."

echo $action

databricks workspace import-dir --overwrite "./notebooks" "$DATABRICKS_WORKSPACE_PROJECT_DIR"

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"



# Criando cluster

action="Criando cluster..."

echo $action

databricks clusters create --json @cluster_config.json

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"




# Criando jobs



echo "-----------------------------------------------------------------------------------------------------------------------"
echo "Deploy Databricks realizado com sucesso!"
echo "-----------------------------------------------------------------------------------------------------------------------"