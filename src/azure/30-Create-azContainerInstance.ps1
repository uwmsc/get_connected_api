cd $PSScriptRoot
. .\Create-AzureResourcesMain.ps1

#todo check if powershell now supports vnets to not have to use azure cli
#log into azure cli
#az login

#specify resource group
$rg = $ResourceGroup
#specify container registry name
$acrName = $ContainerRegistry

#specify container instance name
$aciName = $ContainerInstance

#login to registry
$registry = Get-AzContainerRegistry -Name $acrName -ResourceGroupName $rg
$creds = Get-AzContainerRegistryCredential -Registry $registry
$creds.Password | docker login $registry.LoginServer -u $creds.Username --password-stdin

#specify image
$tag = $DockerImageTag
$newTag = $registry.LoginServer + '/' + $tag

#vnet details
$vnet = $vnet
$vnetAddPrefix = $vnetAddPrefix
$vnetSubnet = $vnetSubnet
$vnetSubnetAddPrefix = $vnetSubnetAddPrefix


#remove if exists
az container delete --name $aciName --resource-group $rg --yes

#create container instance
#note this command may need to be run twice: https://github.com/Azure/azure-cli/pull/17486 

#for testing/troubleshooting purposes. Can comment out or remove for production.
$cmdlineArg = "/bin/sh -c 'echo hello; sleep 100000'"

#creates a string for the environment variables that the az cli command will accept
. .\Parse-IniFile.ps1
$env_vars = Parse-IniFile .\.env_vars | Select-Object -ExpandProperty values
$evs = @()
foreach ($i in $env_vars) { $evs +=  $i.GetEnumerator().ForEach({ "$($_.Name)=$($_.Value)" }) }

#creates the container using the az cli command. 
az container create `
  --name $aciName `
  --resource-group $rg `
  --registry-login-server $registry.LoginServer `
  --registry-username $creds.Username `
  --registry-password $creds.Password `
  --image $newTag `
  --vnet $vnet `
  --vnet-address-prefix $vnetAddPrefix `
  --subnet $vnetSubnet `
  --subnet-address-prefix $vnetSubnetAddPrefix `
  --cpu 1 --memory 1 `
  --command-line $cmdlineArg `
  --environment-variables $evs