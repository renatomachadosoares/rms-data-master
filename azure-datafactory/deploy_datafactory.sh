#!/bin/bash

# FONTE: https://learn.microsoft.com/en-us/azure/data-factory/quickstart-create-data-factory-azure-cli

RESOURCE_GROUP="rsgrmsdms810401"
DATA_FACTORY="dtfrmsdms810401"

az datafactory linked-service create \
--resource-group $RESOURCE_GROUP \
--factory-name $DATA_FACTORY \
--linked-service-name ls_stockquotes \
--properties linkedService/ls_stockquotes.json

az datafactory linked-service create \
--resource-group $RESOURCE_GROUP \
--factory-name $DATA_FACTORY \
--linked-service-name ls_datalake_storage \
--properties linkedService/ls_datalake_storage.json

az datafactory dataset create \
--resource-group $RESOURCE_GROUP \
--dataset-name ds_datalake_storage \
--factory-name $DATA_FACTORY \
--properties dataset/ds_datalake_storage.json

az datafactory dataset create \
--resource-group $RESOURCE_GROUP \
--dataset-name ds_stockquotes \
--factory-name $DATA_FACTORY \
--properties dataset/ds_stockquotes.json

az datafactory pipeline create \
--resource-group $RESOURCE_GROUP \
--factory-name $DATA_FACTORY \
--name pipeline_stockquotes \
--pipeline pipeline/pipeline_stockquotes.json