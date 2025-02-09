#!/bin/bash

# FONTE: https://learn.microsoft.com/en-us/azure/data-factory/quickstart-create-data-factory-azure-cli

# INPUTS

RESOURCE_GROUP=$1
DATA_FACTORY=$2
FUNCTION_APP=$3
STORAGE_ACCOUNT=$4
KEYVAULT=$5
SQLDB_SERVER=$6
SQLDB_DBNAME=$7
SQLDB_ADMUSR=$8
SQLDBPWD_SECRET_NAME=$9
CONTAINER_LAKE=$10
CLIENT_QUOTE_PIPE_EXEC_INTERVAL_MINUTES=$11
CLIENT_BASE_AND_CEPS_PIPE_EXEC_INTERVAL_MINUTES=$12


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
# LINKED SERVICES
##########################################################

action="Criando linked service 'ls_stockquotes'..."

echo $action

# Preparando arquivo de config json a partir do template

awk -v function_app="$FUNCTION_APP" '{
    gsub(/<<FUNCTION_APP>>/, function_app);
    print
}' linkedService/ls_stockquotes.json > config_temp.json

# Executando deploy

az datafactory linked-service create \
--resource-group $RESOURCE_GROUP \
--factory-name $DATA_FACTORY \
--linked-service-name ls_stockquotes \
--properties config_temp.json

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


action="Criando linked service 'ls_datalake_storage'..."

echo $action

# Preparando arquivo de config json a partir do template

awk -v storage_account="$STORAGE_ACCOUNT" '{
    gsub(/<<STORAGE_ACCOUNT>>/, storage_account);
    print
}' linkedService/ls_datalake_storage.json > config_temp.json

# Executando deploy

az datafactory linked-service create \
--resource-group $RESOURCE_GROUP \
--factory-name $DATA_FACTORY \
--linked-service-name ls_datalake_storage \
--properties config_temp.json

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


action="Criando linked service 'ls_keyvault'..."

echo $action

# Preparando arquivo de config json a partir do template

awk -v keyvault="$KEYVAULT" '{
    gsub(/<<KEYVAULT>>/, keyvault);
    print
}' linkedService/ls_keyvault.json > config_temp.json

# Executando deploy

az datafactory linked-service create \
--resource-group $RESOURCE_GROUP \
--factory-name $DATA_FACTORY \
--linked-service-name ls_keyvault \
--properties config_temp.json

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


action="Criando linked service 'ls_dbcustomers'..."

echo $action

# Preparando arquivo de config json a partir do template

awk -v sqldb_server="$SQLDB_SERVER" -v sqldb_dbname="$SQLDB_DBNAME" -v sqldb_admusr="$SQLDB_ADMUSR" -v pwd_secret="$SQLDBPWD_SECRET_NAME" '{
    gsub(/<<SQLDB_SERVER>>/, sqldb_server);
    gsub(/<<SQLDB_DBNAME>>/, sqldb_dbname);
    gsub(/<<SQLDB_ADMUSR>>/, sqldb_admusr);
    gsub(/<<SQLDBPWD_SECRET_NAME>>/, pwd_secret);
    print
}' linkedService/ls_dbcustomers.json > config_temp.json

# Executando deploy

az datafactory linked-service create \
--resource-group $RESOURCE_GROUP \
--factory-name $DATA_FACTORY \
--linked-service-name ls_dbcustomers \
--properties config_temp.json

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


action="Criando linked service 'ls_ceps'..."

echo $action

# Preparando arquivo de config json a partir do template

awk -v function_app="$FUNCTION_APP" '{
    gsub(/<<FUNCTION_APP>>/, function_app);
    print
}' linkedService/ls_ceps.json > config_temp.json

# Executando deploy

az datafactory linked-service create \
--resource-group $RESOURCE_GROUP \
--factory-name $DATA_FACTORY \
--linked-service-name ls_ceps \
--properties config_temp.json

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


##########################################################
# DATASETS
##########################################################


action="Criando dataset 'ds_datalake_storage_quotes'..."

echo $action

# Preparando arquivo de config json a partir do template

awk -v container_lake="$CONTAINER_LAKE" '{
    gsub(/<<CONTAINER_LAKE>>/, container_lake);
    print
}' dataset/ds_datalake_storage_quotes.json > config_temp.json

# Executando deploy

az datafactory dataset create \
--resource-group $RESOURCE_GROUP \
--dataset-name ds_datalake_storage_quotes \
--factory-name $DATA_FACTORY \
--properties config_temp.json

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


action="Criando dataset 'ds_datalake_storage_clients'..."

echo $action

# Preparando arquivo de config json a partir do template

awk -v container_lake="$CONTAINER_LAKE" '{
    gsub(/<<CONTAINER_LAKE>>/, container_lake);
    print
}' dataset/ds_datalake_storage_clients.json > config_temp.json

# Executando deploy

az datafactory dataset create \
--resource-group $RESOURCE_GROUP \
--dataset-name ds_datalake_storage_clients \
--factory-name $DATA_FACTORY \
--properties config_temp.json

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


action="Criando dataset 'ds_dbcustomer_clients'..."

echo $action

az datafactory dataset create \
--resource-group $RESOURCE_GROUP \
--dataset-name ds_dbcustomer_clients \
--factory-name $DATA_FACTORY \
--properties dataset/ds_dbcustomer_clients.json

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


action="Criando dataset 'ds_dbcustomer_ingest_control'..."

echo $action

az datafactory dataset create \
--resource-group $RESOURCE_GROUP \
--dataset-name ds_dbcustomer_ingest_control \
--factory-name $DATA_FACTORY \
--properties dataset/ds_dbcustomer_ingest_control.json

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


action="Criando dataset 'ds_ceps'..."

echo $action

az datafactory dataset create \
--resource-group $RESOURCE_GROUP \
--dataset-name ds_ceps \
--factory-name $DATA_FACTORY \
--properties dataset/ds_ceps.json

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


action="Criando dataset 'ds_datalake_storage_ceps'..."

echo $action

# Preparando arquivo de config json a partir do template

awk -v container_lake="$CONTAINER_LAKE" '{
    gsub(/<<CONTAINER_LAKE>>/, container_lake);
    print
}' dataset/ds_datalake_storage_ceps.json > config_temp.json

# Executando deploy

az datafactory dataset create \
--resource-group $RESOURCE_GROUP \
--dataset-name ds_datalake_storage_ceps \
--factory-name $DATA_FACTORY \
--properties config_temp.json

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


##########################################################
# PIPELINES
##########################################################

action="Criando pipeline 'pipeline_stockquotes'..."

echo $action

az datafactory pipeline create \
--resource-group $RESOURCE_GROUP \
--factory-name $DATA_FACTORY \
--name pipeline_stockquotes \
--pipeline pipeline/pipeline_stockquotes.json

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


action="Criando pipeline 'pipeline_clients_ceps'..."

echo $action

az datafactory pipeline create \
--resource-group $RESOURCE_GROUP \
--factory-name $DATA_FACTORY \
--name pipeline_clients_ceps \
--pipeline pipeline/pipeline_clients_ceps.json

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


action="Forçando a primeira execução do pipeline 'pipeline_stockquotes'..."

echo $action

az datafactory pipeline create-run \
--factory-name $DATA_FACTORY \
--name "pipeline_stockquotes" \
--resource-group $RESOURCE_GROUP


action="Forçando a primeira execução do pipeline 'pipeline_clients_ceps'..."

echo $action

az datafactory pipeline create-run \
--factory-name $DATA_FACTORY \
--name "pipeline_clients_ceps" \
--resource-group $RESOURCE_GROUP


##########################################################
# TRIGGERS
##########################################################

action="Criando trigger pipeline 'trg_pipe_clients_ceps'..."

echo $action

# Preparando arquivo de config json a partir do template

awk -v pipe_interval="$CLIENT_BASE_AND_CEPS_PIPE_EXEC_INTERVAL_MINUTES" '{
    gsub(/<<CLIENT_BASE_AND_CEPS_PIPE_EXEC_INTERVAL_MINUTES>>/, pipe_interval);
    print
}' trigger/trg_pipe_clients_ceps.json > config_temp.json

# Executando deploy

az datafactory trigger create \
--factory-name $DATA_FACTORY \
--resource-group $RESOURCE_GROUP \
--name trg_pipe_clients_ceps \
--properties config_temp.json

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


action="Criando trigger pipeline 'trg_pipe_quotes'..."

echo $action

# Preparando arquivo de config json a partir do template

awk -v pipe_interval="$CLIENT_QUOTE_PIPE_EXEC_INTERVAL_MINUTES" '{
    gsub(/<<CLIENT_QUOTE_PIPE_EXEC_INTERVAL_MINUTES>>/, pipe_interval);
    print
}' trigger/trg_pipe_quotes.json > config_temp.json

# Executando deploy

az datafactory trigger create \
--factory-name $DATA_FACTORY \
--resource-group $RESOURCE_GROUP \
--name trg_pipe_quotes \
--properties config_temp.json

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


action="Start da trigger pipeline 'trg_pipe_clients_ceps'..."

echo $action

az datafactory trigger start \
--factory-name $DATA_FACTORY \
--resource-group $RESOURCE_GROUP \
--name trg_pipe_clients_ceps

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


action="Start da trigger pipeline 'trg_pipe_quotes'..."

echo $action

az datafactory trigger start \
--factory-name $DATA_FACTORY \
--resource-group $RESOURCE_GROUP \
--name trg_pipe_quotes

check_return "$action"

echo "-----------------------------------------------------------------------------------------------------------------------"


rm config_temp.json

echo "-----------------------------------------------------------------------------------------------------------------------"
echo "Deploy Datafactory realizado com sucesso!"
echo "-----------------------------------------------------------------------------------------------------------------------"
