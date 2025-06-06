#!/bin/bash

source ./config.sh

#########################################################
#
# Este case usa como provedor de recursos na nuvem o 
# Microsoft Azure.
#
# Pré-requisito para execução:
#
# Login na Azure através do comando abaixo:
#
# az login --tenant <TENANT-ID>
#
# IMPORTANTE: No processo de login utilizar a conta Global 
# (em alguns casos é definida pela conta com email #EXT#)
#
#########################################################


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

# Permite a instalação de extensões dinamicamente
az config set extension.use_dynamic_install=yes_without_prompt

# Registra o resource 'Microsoft.sql' para que possa ser instanciado
az provider register --namespace Microsoft.Sql


#########################################################
# Instanciando os recursos
#########################################################

echo -e "\n*****************************************************************************************"
echo "Provisão de recursos Azure"
echo -e "*****************************************************************************************\n"


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
--hns true
#--hierarchical-namespace true

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


action="Criando diretório 'mngt' no container do lake '$CONTAINER_LAKE'..."

echo $action

az storage fs directory create -n "mngt" -f $CONTAINER_LAKE --account-name $STORAGE_ACCOUNT --auth-mode login

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


# ***************************************************************************************************************************
# SQL DATABASE
# ***************************************************************************************************************************

action="Criando Azure SQL Database Server..."

echo $action

az sql server create \
--name $SQLDB_SERVER \
--resource-group $RESOURCE_GROUP \
--location "$LOCATION" \
--assign-identity \
--identity-type SystemAssigned \
--admin-user $SQLDB_ADMUSR \
--admin-password $SQLDB_PWD

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


action="Criando Database..."

echo $action

# Cria Database no free tier

az sql db create \
-g $RESOURCE_GROUP \
-s $SQLDB_SERVER \
-n $SQLDB_DBNAME \
-e GeneralPurpose \
-f Gen5 \
-c 1 \
--compute-model Serverless \
--use-free-limit \
--free-limit-exhaustion-behavior AutoPause \
--backup-storage-redundancy Local

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


action="Criando regra de firewall no DB para acesso pelos recursos..."

echo $action

# Cria uma regra de firewall para permitir o acesso ao banco por todos os recursos

az sql server firewall-rule create \
--resource-group $RESOURCE_GROUP \
--server $SQLDB_SERVER \
--name rl_access_resources \
--start-ip-address 0.0.0.0 \
--end-ip-address 0.0.0.0

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


# SYSTEM MANAGED IDENTITY DATA FACTORY 

action="Obtendo a managed identity do data factory..."

echo $action

mng_ident_id_dtf=$(grep -oP '(?<="principalId": ")[^"]*' <<< $(az datafactory show --resource-group $RESOURCE_GROUP --name $DATA_FACTORY))

check_return "$action"

echo $mng_ident_id_dtf

echo "-----------------------------------------------------------------------------------------------------------------------"


# ROLE DATA CONTRIBUTOR NO STORAGE ACCOUNT PARA O DATA FACTORY

# Atribuindo a role de 'storage blob data contributor' para a system managed identity do Data Factory no Storage account. 

action="Setando role 'data contributor' para o data factory no storage account..."

echo $action

az role assignment create \
--assignee $mng_ident_id_dtf \
--role 'Storage Blob Data Contributor' \
--scope subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACCOUNT

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


action="Setando role 'SQL DB Contributor' para o data factory no database SQL..."

echo $action

az role assignment create \
--assignee $mng_ident_id_dtf \
--role 'SQL DB Contributor' \
--scope subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Sql/servers/$SQLDB_SERVER

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


# ***************************************************************************************************************************
# EVENT HUBS
# ***************************************************************************************************************************

action="Criando event hub namespace $EVENTHUBS_NAMESPACE..."

echo $action

az eventhubs namespace create \
--name $EVENTHUBS_NAMESPACE \
--resource-group $RESOURCE_GROUP \
--mi-system-assigned true \
-l "$LOCATION"

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"

sleep 20

# SYSTEM MANAGED IDENTITY EVENT HUB NAMESPACE

# Obtem essa identidade para posteriormente ser atribuida a ela a role 'Storage Blob Data Contributor' no storage account

action="Obtendo a managed identity do event hub namespace..."

echo $action

mng_ident_id_evh=$(grep -oP '(?<="principalId": ")[^"]*' <<< $(az eventhubs namespace show --name $EVENTHUBS_NAMESPACE --resource-group $RESOURCE_GROUP))

check_return "$action"

echo $mng_ident_id_evh

echo "-----------------------------------------------------------------------------------------------------------------------"


# ROLE DATA CONTRIBUTOR NO STORAGE ACCOUNT PARA O EVENT HUB NAMESPACE

# Atribuindo a role de 'storage blob data contributor' para a system managed identity do Event Hub no Storage account. 

action="Setando role 'data contributor' para o event hub no storage account..."

echo $action

az role assignment create \
--assignee $mng_ident_id_evh \
--role 'Storage Blob Data Contributor' \
--scope subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACCOUNT

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"

sleep 20


# Criação do tópico para ingestao dos dados de 'orders'

action="Criando event hub tópico $EVENTHUBS_TOPIC com capture ativo..."

echo $action

az eventhubs eventhub create \
--name $EVENTHUBS_TOPIC \
--resource-group $RESOURCE_GROUP \
--namespace-name $EVENTHUBS_NAMESPACE \
--partition-count 1 \
--enable-capture true \
--destination-name EventHubArchive.AzureBlockBlob \
--archive-name-format "raw/orders/event_hub={Namespace}/topic={EventHub}/dat_ref_carga={Year}-{Month}-{Day}/{Hour}_{Minute}_{Second}_{PartitionId}" \
--storage-account $STORAGE_ACCOUNT \
--blob-container $CONTAINER_LAKE \
--capture-interval $(($CLIENT_QUOTE_PIPE_EXEC_INTERVAL_MINUTES * 60)) \
--mi-system-assigned true \
--skip-empty-archives true 

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

sleep 15    # Dorme alguns segundos para garantir que a publicação das functions não falhe

echo "-----------------------------------------------------------------------------------------------------------------------"


# SYSTEM MANAGED IDENTITY AZURE FUNCTION

# Posteriormente será atribuida a essa identidade a role de 'Azure Event Hubs Data Owner' no event hubs

action="Criando system managed identity para a azure function app '$FUNCTION_APP'..."

echo $action

mng_ident_id_azf=$(grep -oP '(?<="principalId": ")[^"]*' <<< $(az webapp identity assign --name $FUNCTION_APP --resource-group $RESOURCE_GROUP)) 

check_return "$action"

echo $mng_ident_id_azf

echo "-----------------------------------------------------------------------------------------------------------------------"

sleep 15


action="Setando role 'Azure Event Hubs Data Owner' para o azure function no event hubs..."

echo $action

az role assignment create \
--assignee $mng_ident_id_azf \
--role 'Azure Event Hubs Data Owner' \
--scope subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.EventHub/namespaces/$EVENTHUBS_NAMESPACE

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


action="Setando role 'SQL DB Contributor' para o azure function no database SQL..."

echo $action

az role assignment create \
--assignee $mng_ident_id_azf \
--role 'SQL DB Contributor' \
--scope subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Sql/servers/$SQLDB_SERVER

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


# ***************************************************************************************************************************
# AZURE KEY VAULT
# ***************************************************************************************************************************

action="Criando azure key vault '$KEYVAULT'..."

echo $action

az keyvault create \
--name $KEYVAULT \
--resource-group $RESOURCE_GROUP \
--location "$LOCATION"

check_return "$action"

sleep 10

echo "-----------------------------------------------------------------------------------------------------------------------"


action="Define para o meu usuário permissão de gerenciar o key vault..."

echo $action

az role assignment create \
--role "Key Vault Secrets Officer" \
--assignee $USER_OBJECT_ID \
--scope subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.KeyVault/vaults/$KEYVAULT

check_return "$action"

sleep 10

echo "-----------------------------------------------------------------------------------------------------------------------"


action="Setando role 'Key Vault Secrets User' para o data factory no key vault..."

echo $action

az role assignment create \
--role "Key Vault Secrets Officer" \
--assignee $mng_ident_id_dtf \
--scope subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.KeyVault/vaults/$KEYVAULT

check_return "$action"

sleep 10

echo "-----------------------------------------------------------------------------------------------------------------------"


action="Criando a secret com a senha do DB SQL no key vault..."

echo $action

az keyvault secret set \
--vault-name $KEYVAULT \
--name "$SQLDBPWD_SECRET_NAME" \
--value "$SQLDB_PWD"

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


########################################################
# Publicando as aplicações
########################################################

echo -e "\n*****************************************************************************************"
echo "Publicação das aplicações"
echo -e "*****************************************************************************************\n"

# ----------------------------------
# PUBLICAÇÃO AZURE FUNCTIONS
# ----------------------------------

action="Publicando azure functions..."

echo $action

cd azure-functions

./deploy_azure_functions.sh \
"$FUNCTION_APP" \
"$RESOURCE_GROUP" \
"$EVENTHUBS_NAMESPACE" \
"$EVENTHUBS_TOPIC" \
"$SQLDB_SERVER" \
"$SQLDB_DBNAME" \
"$SQLDB_ADMUSR" \
"$SQLDB_PWD" \
"$ORDER_DATA_GENERATOR_INTERVAL_MINUTES" \
"$CLIENT_BASE_DATA_GENERATOR_INTERVAL_MINUTES"

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"

cd -

sleep 60


# ----------------------------------
# BASE DE DADOS SQL
# ----------------------------------

# Para a criação e carga dos dados que fazem parte da base SQL usada como uma das fontes de dados de ingestão uso duas 
# Azure Functions, uma para a execução dos DDLs e outra para a execução dos DMLs. Essas funcões estão definidas no 
# projeto de functions na pasta 'azure-functions' arquivo 'function_app.py'

echo "Criando a base de dados de clientes..."

echo $action

curl -k https://$FUNCTION_APP.azurewebsites.net/api/createdbcustomer

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"

sleep 10


echo "Carregando a base de dados de clientes..."

echo $action

curl -k https://$FUNCTION_APP.azurewebsites.net/api/loaddbcustomer

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


# ----------------------------------
# PUBLICACAO PIPELINES DATA FACTORY
# ----------------------------------

cd azure-datafactory

echo "Instalando pipeline datafactory..."

echo $action

./deploy_datafactory.sh \
"$RESOURCE_GROUP" \
"$DATA_FACTORY" \
"$FUNCTION_APP" \
"$STORAGE_ACCOUNT" \
"$KEYVAULT" \
"$SQLDB_SERVER" \
"$SQLDB_DBNAME" \
"$SQLDB_ADMUSR" \
"$SQLDBPWD_SECRET_NAME" \
"$CONTAINER_LAKE" \
"$CLIENT_QUOTE_PIPE_EXEC_INTERVAL_MINUTES" \
"$CLIENT_BASE_AND_CEPS_PIPE_EXEC_INTERVAL_MINUTES"

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"

cd -


# ----------------------------------
# DATABRICKS
# ----------------------------------


# Devido a complexidade do processo de criação do workspace Databricks todos os passos foram disponibilizados em um script separado.

cd azure-databricks

echo "Instalando workspace Databricks..."

echo $action

./deploy_databricks.sh \
"$SUBSCRIPTION_ID" \
"$RESOURCE_GROUP" \
"$DATABRICKS" \
"$STORAGE_ACCOUNT" \
"$CONTAINER_LAKE" \
"$LOCATION" \
"$DATABRICKS_ACCESS_CONECTOR" \
"$DATABRICKS_UNITY_CATALOG_NAME" \
"$DATABRICKS_WORKSPACE_PROJECT_DIR" \
"$DATABRICKS_UNITY_CREDENTIAL_NAME" \
"$DATABRICKS_NODE_TYPE" \
"$DATABRICKS_SPARK_VERSION" \
"$DATABRICKS_RUN_JOB_AS" \
"$DATABRICKS_CREATE_CLUSTER_DEMO" \
"$DATABRICKS_NODE_TYPE_CLUSTER_DEMO"


check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"

cd -


echo -e "\n\nDeploy realizado com sucesso!"

exit 0