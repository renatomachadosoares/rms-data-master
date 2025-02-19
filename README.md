# Case Data Master - Corretora de Valores

O case visa demonstrar a implantação de um projeto de Delta Lake para uma corretora de valores ficticia, passando pela aquisição/ingestão dos dados, processamento e monitoramento dos processos.

O projeto utiliza recursos disponibilizados pelo provedor de nuvem Microsoft Azure.

Este case foi utilizado no processo de obtenção da badge 'Data Master' na [F1rst Tecnologia](https://www.f1rst.com.br/first/#/) uma empresa do grupo [Santander](https://www.santander.com.br/)


## Pré-requisitos

Para a implantação do projeto são necessários os seguintes softwares:

- [PYTHON 3.11](https://www.python.org/downloads/release/python-3110/)
- [AZURE CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-windows?pivots=winget)
- [AZURE FUNCTIONS CORE TOOLS](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=windows%2Cisolated-process%2Cnode-v4%2Cpython-v2%2Chttp-trigger%2Ccontainer-apps&pivots=programming-language-python#install-the-azure-functions-core-tools)
- [DATABRICKS CLI](https://docs.databricks.com/en/dev-tools/cli/install.html#source-install)
- Interpretador Bash (sugestão para ambientes Windows [Git Bash](https://git-scm.com/downloads/win))

Azure account

É necessário possuir uma Azure account com uma subscrição ativa em qualquer uma das modalidades: 'Free Tier' ou 'Pay as you go'. Ver: [Azure account](https://azure.microsoft.com/en-us/pricing/purchase-options/azure-account)


## Login Azure account

No prompt Bash no diretório raiz do projeto, faça o login na sua Azure account através do comando abaixo, quando solicitado selecione a subscription desejada.

  az login --tenant "<TENANT_ID>"

Obtenha o <TENANT_ID> através do [portal Azure](https://portal.azure.com/#home) -> Tenant Properties


## Estrutura dos scripts de deploy

Os scripts de deploy apresentam a estrutura mostrada abaixo, onde os principais recursos possuem scripts de deploy separados para melhor organização, porém todos são invocados a partir do script principal 'deploy_script.sh' sem necessidade de que sejam invocados separadamente.

![Estrutura deploy](doc-images/estrutura_scripts_deploy.PNG)


## Script de configuração

Edite o arquivo 'config.sh' com os parâmetros necessários para o deploy. 

O arquivo possui comentários para guiar no preenchimento de cada parâmetro.


## Execução do deploy

Uma vez definidos os parâmetros no arquivo 'config.sh', execute o script de deploy.

O comando abaixo inicia a execução do deploy na Azure dos recursos necessários para o case.

  ./deploy_script.sh > deploy_output.log 2>&1

No comando acima toda a saída do script de deploy é redirecionada para o arquivo 'deploy_output.log' no diretório raiz do projeto caso deseje consultá-lo após o fim do deploy ou para debug de erros.






## Melhorias desejadas

- Deploy de recursos azure utilizando ARM templates
- Utilização de service principal para execução de jobs Databricks
- Substituir uso do comando grep pelo programa linux 'jq' no tratamento de retornos json nos scripts de implantação
- Substituir uso do Databricks CLI pela API Rest
- Substituir uso de Capture nos event hubs por job databricks lendo diretamente o tópico de ingestão dos status das ordens de compra e venda do cliente
  o Capture é responsável pelo maior custo no namespace
- Usar variáveis globais no data factory e definir seus valores usando azure cli, substituir pelo processo atual que usa awk e json templates para definir parâmetros para os elementos adf.
