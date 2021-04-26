cd $PSScriptRoot
. .\Create-AzureResourcesMain.ps1

$sourceVnet = $vnet
$targetVnet = $targetVnet
$sourceResourceGroup = $ResourceGroup
$targetResourceGroup = $targetResourceGroup
# get Vnets
$vnet1 = Get-AzVirtualNetwork -Name $sourceVnet -ResourceGroupName $sourceResourceGroup
$vnet2 = Get-AzVirtualNetwork -Name $targetVnet -ResourceGroupName $targetResourceGroup

# Peer VNet1 to VNet2.
Add-AzVirtualNetworkPeering -Name "Link$($sourceVnet)_To_$($peerVnet)" -VirtualNetwork $vnet1 -RemoteVirtualNetworkId $vnet2.Id 

# Peer VNet2 to VNet1.
Add-AzVirtualNetworkPeering -Name "Link$($peerVnet)_To_$($sourceVnet)" -VirtualNetwork $vnet2 -RemoteVirtualNetworkId $vnet1.Id -AllowGatewayTransit

