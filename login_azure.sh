#!/bin/bash

# Autenticação (ver: https://learn.microsoft.com/en-us/cli/azure/authenticate-azure-cli)

# Setando a subscription default
az account set --subscription "8071356f-927f-41b5-a491-71b837d0d882"

# Login interativo
az login --tenant "8b6570ad-95be-4819-b45b-7734399ce1dc"
