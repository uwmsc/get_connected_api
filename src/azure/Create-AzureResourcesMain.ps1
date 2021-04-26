function Get-AzLoginStatus
{
    $context = Get-AzContext

    if (!$context) 
    {
        Connect-AzAccountb -UseDeviceAuthentication
    } 
    else 
    {
        Write-Host "$($context.Account) already connected to $($context.Subscription) "
    }
}
#login to azure if not already
Get-AzLoginStatus

# #todo check if powershell now supports vnets to not have to use azure cli
# #log into azure cli
az login 

#set parameters
#docker variables
$ResourceGroup = '<name>'
$ContainerRegistry = '<name>'
$DockerImageTag = '<name>'
$ContainerInstance = '<name>'

#networking variables (assuming separate vnets)
$vnet = '<name>'
$vnetAddPrefix = '<ip>/<pool>'
$vnetSubnet = '<name>'
$vnetSubnetAddPrefix = '<ip>/<pool>'
$targetVnet = '<name>'
$targetResourceGroup = '<name>'