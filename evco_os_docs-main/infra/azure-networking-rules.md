# standard inbound port rules for our VMs
```console
$ nsg_name=MAIN-EVWORKS-OS-PROD-nsg
$ rg=EVCO_PROD_RG

$ az network nsg rule create --resource-group $rg --nsg-name $nsg_name --priority 310 --source-port-ranges '*' --destination-port-ranges 80 --protocol Tcp --access Allow -n Port_80

$ az network nsg rule create --resource-group $rg --nsg-name $nsg_name --priority 320 --source-port-ranges '*' --destination-port-ranges 443 --protocol Tcp --access Allow -n Port_443

$ az network nsg rule create --resource-group $rg --nsg-name $nsg_name --priority 330 --source-port-ranges '*' --destination-port-ranges 22 --protocol '*' --access Allow -n AllowAnyCustom22Inbound
```

# one liner
```
nsg_name=MAIN-EVWORKS-OS-PROD-nsg;rg=EVCO_PROD_RG;az network nsg rule create --resource-group $rg --nsg-name $nsg_name --priority 310 --source-port-ranges '*' --destination-port-ranges 80 --protocol Tcp --access Allow -n Port_80;az network nsg rule create --resource-group $rg --nsg-name $nsg_name --priority 320 --source-port-ranges '*' --destination-port-ranges 443 --protocol Tcp --access Allow -n Port_443;az network nsg rule create --resource-group $rg --nsg-name $nsg_name --priority 330 --source-port-ranges '*' --destination-port-ranges 22 --protocol '*' --access Allow -n AllowAnyCustom22Inbound
```