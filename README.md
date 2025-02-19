# Case Data Master - Corretora de Valores

O case visa demonstrar a implantação de um projeto de Delta Lake para uma corretora de valores ficticia, passando pela aquisição/ingestão dos dados, processamento e monitoramento dos processos.

O projeto utiliza recursos disponibilizados pelo provedor de nuvem Microsoft Azure.

Este case foi utilizado no processo de obtenção da badge 'Data Master' na [F1rst Tecnologia](https://www.f1rst.com.br/first/#/) uma empresa do grupo [Santander](https://www.santander.com.br/)

## Pré-requisitos

Para a implantação do projeto são necessários os seguintes softwares:

- [PYTHON 3.11]()
- [AZURE CLI]()
- [AZURE FUNCTIONS]()
- [DATABRICKS CLI](https://docs.databricks.com/en/dev-tools/cli/install.html#source-install)
- Interpretador Bash


-- Deploy

Em um prompt bash faça login na azure:

az login --tenant <TENANT-ID>

Nota: O <TENANT-ID> pode ser obtido através do 'Tenant properties' no portal Azure.

Selecione a subscription quando solicitado.


## Estrutura do deploy

![Estrutura deploy](doc-images/estrutura_scripts_deploy.PNG)

Execute o script de deploy no diretório raiz do projeto:

./deploy_script.sh

Caso deseje redirecionar a saida do script de deploy para um arquivo de log use o exemplo abaixo:

./deploy_script.sh > deploy_output.log 2>&1


-- Functions

Get stocks:
https://afarmsdms810401.azurewebsites.net/api/stockquotes


-- Melhorias desejadas

- Deploy de recursos azure utilizando ARM templates
- Utilização de service principal para execução de jobs Databricks
- Substituir uso do comando grep pelo programa linux 'jq' no tratamento de retornos json nos scripts de implantação
- Substituir uso do Databricks CLI pela API Rest
- Substituir uso de Capture nos event hubs por job databricks lendo diretamente o tópico de ingestão dos status das ordens de compra e venda do cliente
  o Capture é responsável pelo maior custo no namespace
- Usar variáveis globais no data factory e definir seus valores usando azure cli, substituir pelo processo atual que usa awk e json templates para definir parâmetros para os elementos adf.
