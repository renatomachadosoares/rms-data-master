#!/bin/bash

RESOURCE_GROUP="rsgrmsdms810401"
STORAGE_ACCOUNT="starmsdms810401"

#az resource show -g $RESOURCE_GROUP --resource-type Microsoft.Storage/storageAccounts -n $STORAGE_ACCOUNT

test_metainfo=$(az resource show -g $RESOURCE_GROUP --resource-type Microsoft.Storage/storageAccounts -n $STORAGE_ACCOUNT)


value=$(grep -oP '(?<="creationTime": ")[^"]*' <<< $test_metainfo)


url="hora criacao=$value.teste"

echo "$url"

echo "-------------------------------------------------------"

echo $value