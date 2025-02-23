#########################################################
# SCRIPT DEPLOY - PARAMETROS AZURE
#########################################################

# Geral

SUBSCRIPTION_ID="8071356f-927f-41b5-a491-71b837d0d882"          # ID da subscrição Azure
LOCATION="Brazil South"                                         # Localidade onde se deseja provisionar os recursos na Azure
RESOURCE_GROUP="rsgrmsdms810401"                                # Nome do grupo de recursos a ser criado para execução do case

# User

USER_PRINCIPAL_NAME="renatomachadosoares_hotmail.com#EXT#@renatomachadosoareshotmail.onmicrosoft.com"   # 'User principal name' obtido no portal azure em 'Microsoft Entra ID' -> Users
USER_OBJECT_ID="2d59d779-8aa4-468c-8e4a-59b458dc971c"           # 'Object ID' do usuário definido acima, obtido no portal azure em 'Microsoft Entra ID' -> Users

# Storage

STORAGE_ACCOUNT="starmsdms810401"                               # Nome do storage account a ser criado
CONTAINER_LAKE="ctnlake"                                        # Nome do container a ser criado no storage account para uso das aplicações

# Data factory

DATA_FACTORY="dtfrmsdms810401"                                  # Nome do data factory a ser criado

# Function App

FUNCTION_APP="afarmsdms810401"                                  # Nome do azure function app a ser criado

# Event Hubs

EVENTHUBS_NAMESPACE="evhnmprmsdms810401"                        # Nome do namespace event hubs a ser criado
EVENTHUBS_TOPIC="evhorders"                                     # Nome do tópico event hubs a ser criado no namespace definido acima

# SQL Server

SQLDB_SERVER="sdbrmsdms810401"                                  # Nome do SQL Server a ser criado
SQLDB_ADMUSR="sqldbrms_usr"                                     # Nome do usuário admin do SQL Server
SQLDB_PWD="pwdD8*DMS#"                                          # Senha do SQL Server para o usuário admin. Regra de complexidade da senha: https://learn.microsoft.com/en-us/previous-versions/azure/jj943764(v=azure.100)?redirectedfrom=MSDN
SQLDB_DBNAME="CUSTOMER"                                         # Nome do Database a ser criado no SQL server para cadastro da base ficticia de clientes.

# Key Vault

KEYVAULT="akvrmsdms810401"                                      # Nome do Keyvault a ser criado
SQLDBPWD_SECRET_NAME="sqldbcustomer-pwd"                        # Nome da chave no keyvault para acesso a senha do SQL Database

# Databricks

DATABRICKS="adbrmsdms810401"                                    # Nome da instância Databricks a ser criada
DATABRICKS_ACCESS_CONECTOR="adbacrmsdms810401"                  # Nome do conector de acesso databricks ao storage account
DATABRICKS_UNITY_CATALOG_NAME="datamaster"                      # Nome do Catálogo Unity a ser criado
DATABRICKS_UNITY_CREDENTIAL_NAME="dm-credential"                # Nome da credencial Azure a ser criada para acesso ao storage account 
DATABRICKS_WORKSPACE_PROJECT_DIR="//Shared/data-master-case"    # Path base para o deploy dos notebooks Databricks
DATABRICKS_NODE_TYPE="Standard_F4"                              # Tipo de instância a ser utilizada para criação do cluster single node para execução do job databricks
DATABRICKS_SPARK_VERSION="15.4.x-scala2.12"                     # Runtime Databricks a ser utlizado para criação do cluster
DATABRICKS_RUN_JOB_AS=$USER_PRINCIPAL_NAME                      # Usuário Databricks utilizado para execução do job, o valor default é o USER_PRINCIPAL_NAME definido na seção de configuração 'User' 
DATABRICKS_CREATE_CLUSTER_DEMO=true                             # Indica se o script deve ou não criar um cluster Databricks all-purpose para demonstração do case
DATABRICKS_NODE_TYPE_CLUSTER_DEMO="Standard_F4"                 # Tipo de instância a ser utilizada para criação do cluster all-purpose para demonstracao do case


#########################################################
# INTERVALOS DE EXECUÇÂO PIPES ADF E SIMULADORES DE DADOS 
#########################################################

ORDER_DATA_GENERATOR_INTERVAL_MINUTES="3"                       # (regra: Deve ser maior que zero e menor que 60) Frequência com que são gerados dados simulados de atualização dos preços das ações
CLIENT_BASE_DATA_GENERATOR_INTERVAL_MINUTES="10"                # (regra: Deve ser maior que zero e menor que 60) Frequência com que são gerados dados simulados de atualização da base de clientes
CLIENT_QUOTE_PIPE_EXEC_INTERVAL_MINUTES="3"                     # Frequência com que é executado o pipeline ADF de carga dos dados simulados de atualização da carteira de ações dos clientes
CLIENT_BASE_AND_CEPS_PIPE_EXEC_INTERVAL_MINUTES="10"            # Frequência com que é executado o pipeline ADF de carga dos dados simulados de cadastro de clientes e base de CEPs
