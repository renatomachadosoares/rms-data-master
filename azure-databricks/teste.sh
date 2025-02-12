CONTAINER_LAKE="ctnlake"
STORAGE_ACCOUNT="starmsdms810401"
DATABRICKS_UNITY_CATALOG_NAME="datamaster"                      # (NAO ALTERAR) Nome do Catálogo Unity
DATABRICKS_UNITY_CREDENTIAL_NAME="dm-credential"                # 
DATABRICKS_WORKSPACE_PROJECT_DIR="//Shared/data-master-case"    # (NAO ALTERAR) Path base para o deploy dos notebooks Databricks
DATABRICKS_NODE_TYPE="Standard_F4"
DATABRICKS_SPARK_VERSION="15.4.x-scala2.12"
DATABRICKS_RUN_JOB_AS="renatomachadosoares_hotmail.com#ext#@renatomachadosoareshotmail.onmicrosoft.com"

export DATABRICKS_TOKEN="dapidfb0820896fe40396346036c8f5e4670"
export DATABRICKS_HOST="https://adb-3065085525844348.8.azuredatabricks.net/"


# awk -v sv="$DATABRICKS_SPARK_VERSION" -v wt="$DATABRICKS_WORKER_NODE_TYPE" -v dt="$DATABRICKS_DRIVER_NODE_TYPE" -v nw="$DATABRICKS_NUM_WORKERS" -v ctn="$CONTAINER_LAKE" -v sa="$STORAGE_ACCOUNT" -v ucred="$DATABRICKS_UNITY_CREDENTIAL_NAME" -v ucat="$DATABRICKS_UNITY_CATALOG_NAME" '{
#     gsub(/<<DATABRICKS_SPARK_VERSION>>/, sv);
#     gsub(/<<DATABRICKS_WORKER_NODE_TYPE>>/, wt);
#     gsub(/<<DATABRICKS_DRIVER_NODE_TYPE>>/, dt);
#     gsub(/<<DATABRICKS_NUM_WORKERS>>/, nw);
#     gsub(/<<CONTAINER_LAKE>>/, ctn);
#     gsub(/<<STORAGE_ACCOUNT>>/, sa);
#     gsub(/<<DATABRICKS_UNITY_CREDENTIAL_NAME>>/, ucred);
#     gsub(/<<DATABRICKS_UNITY_CATALOG_NAME>>/, ucat);
#     print
# }' cluster_config.json > config_temp.json

# # Executando deploy

# echo "Criando cluster..."

# databricks clusters create --json @config_temp.json --no-wait


# # Obtendo cluster ID

# echo "Obtendo id do cluster..."

# cluster_id=$(grep -oP '(?<="cluster_id": ")[^"]*' <<< $(databricks clusters list -o json))

# echo "Id do cluster criado: $cluster_id"


# Criando o workflow

# Remove as barras iniciais do workdir

WORKSPACE_DIR="${DATABRICKS_WORKSPACE_PROJECT_DIR:2}"

# Preparando arquivo de config json a partir do template

awk -v wd="$WORKSPACE_DIR" -v sv="$DATABRICKS_SPARK_VERSION" -v ucat="$DATABRICKS_UNITY_CATALOG_NAME" -v nt="$DATABRICKS_NODE_TYPE" -v ctn="$CONTAINER_LAKE" -v sa="$STORAGE_ACCOUNT" -v ucred="$DATABRICKS_UNITY_CREDENTIAL_NAME" -v ra="$DATABRICKS_RUN_JOB_AS" '{
    gsub(/<<WORKSPACE_DIR>>/, wd);
    gsub(/<<DATABRICKS_SPARK_VERSION>>/, sv);
    gsub(/<<DATABRICKS_UNITY_CATALOG_NAME>>/, ucat);
    gsub(/<<DATABRICKS_NODE_TYPE>>/, nt);
    gsub(/<<CONTAINER_LAKE>>/, ctn);
    gsub(/<<STORAGE_ACCOUNT>>/, sa);
    gsub(/<<DATABRICKS_UNITY_CREDENTIAL_NAME>>/, ucred);  
    gsub(/<<DATABRICKS_RUN_JOB_AS>>/, ra);
    print
}' job_config.json > config_temp.json

# Executando o deploy

echo "Criando o job..."

resp=$(databricks jobs create --json @config_temp.json)

echo $resp


# Obtendo job ID

echo "Obtendo ID do job..."

job_id=$(grep -oP '"job_id":\s*\K\d+' <<< $resp)

echo "Id do job criado: $job_id"



# # Start do job

# echo "Iniciando o job..."

# databricks jobs run-now $job_id --no-wait

# echo "Fim"