#!/bin/bash

UNITY_CREDENTIAL_NAME="teste"
SUBSCRIPTION_ID="123-123"
RESOURCE_GROUP="1234s"
DATABRICKS_ACCESS_CONECTOR="1452-1234-543"

json_req="'{\"name\":\"$UNITY_CREDENTIAL_NAME\",\"azure_managed_identity\": {\"access_connector_id\": \"/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Databricks/accessConnectors/$DATABRICKS_ACCESS_CONECTOR\"}}'"

echo $json_req

json="'$json_req'"

echo $json


req_json='{"name": "'$UNITY_CREDENTIAL_NAME'","azure_managed_identity": {"access_connector_id": "'"/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Databricks/accessConnectors/$DATABRICKS_ACCESS_CONECTOR"'}}'

echo $req_json
