cd $PSScriptRoot
. .\Create-AzureResourcesMain.ps1

$rg = $ResourceGroup
#specify container registry name
$acrName = $ContainerRegistry
#login to registry
$registry = Get-AzContainerRegistry -Name $acrName -ResourceGroupName $rg
$creds = Get-AzContainerRegistryCredential -Registry $registry
$creds.Password | docker login $registry.LoginServer -u $creds.Username --password-stdin

#create image tag
$tag = $DockerImageTag
$newTag = $registry.LoginServer + '/' + $tag

#build and push image
docker build . -t $newTag
docker push $newTag