cd $PSScriptRoot
. .\Create-AzureResourcesMain.ps1

    #specify resource group 
    $rg = $ResourceGroup
    #specify container registry name
    $acrName = $ContainerRegistry
    #create container registry
    $registry = New-AzContainerRegistry -ResourceGroupName $rg -Name $acrName -EnableAdminUser -Sku Basic
    #login to registry
    $registry = Get-AzContainerRegistry -Name $acrName -ResourceGroupName $rg
    $creds = Get-AzContainerRegistryCredential -Registry $registry
    $creds.Password | docker login $registry.LoginServer -u $creds.Username --password-stdin
