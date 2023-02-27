# decomissioning a station or company
TODO:
- to turn into a script that uses a company ID
using GLS as example

## 1. get the company
```python
from customer.models import Company
gls_company = Company.objects.filter(name__iregex="Grocery")
gls_id = gls_company.pk
```

## 2. use company to delete `Member` and `CompanyCustomerPortalModule`
```python
from customer.models import Member,CompanyCustomerPortalModule
from chargingservice.models import ChargingOrder

members = Member.objects.filter(company_id=gls_id)

ChargingOrder.objects.filter(member_id__in=[r.id for r in members]).delete()

CompanyCustomerPortalModule.objects.filter(company_id=gls_id).delete()

members.delete()
```


## 3. delete pile related (delete those with protected relationships)
```python
from station.models import Station,Pile,PileOCPPMessageLog
from chargingservice.models import ChargingTransaction,PileHourlyUtilization

stations = Station.objects.filter(company_id=gls_id)
piles = Pile.objects.filter(station_id__in=[r.id for r in stations])

PileOCPPMessageLog.objects.filter(pile_id__in=[r.id for r in piles]).delete()
ChargingTransaction.objects.filter(pile_id__in=[r.id for r in piles]).delete()
PileHourlyUtilization.objects.filter(pile_id__in=[r.id for r in piles]).delete()
piles.delete()
stations.delete()
gls_company.delete()
```


# decomission company function:
```python
from customer.models import Company,Member,CompanyCustomerPortalModule
from station.models import Station,Pile,PileOCPPMessageLog
from chargingservice.models import ChargingOrder,ChargingTransaction,PileHourlyUtilization

def decommissionCompany(companyPk):
    deletedRowCountDict = {}
    # prune customer models
    members = Member.objects.filter(company_id=companyPk)
    deletedRowCountDict["ChargingOrder"] = ChargingOrder.objects.filter(member_id__in=[r.id for r in members]).delete()
    deletedRowCountDict["CompanyCustomerPortalModule"] = CompanyCustomerPortalModule.objects.filter(company_id=companyPk).delete()
    deletedRowCountDict["Member"] = members.delete()

    # prune station and piles
    stations = Station.objects.filter(company_id=companyPk)
    piles = Pile.objects.filter(station_id__in=[r.id for r in stations])

    deletedRowCountDict["PileOCPPMessageLog"] = PileOCPPMessageLog.objects.filter(pile_id__in=[r.id for r in piles]).delete()
    deletedRowCountDict["ChargingTransaction"] = ChargingTransaction.objects.filter(pile_id__in=[r.id for r in piles]).delete()
    deletedRowCountDict["PileHourlyUtilization"] = PileHourlyUtilization.objects.filter(pile_id__in=[r.id for r in piles]).delete()
    deletedRowCountDict["Pile"] = piles.delete()
    deletedRowCountDict["Station"] = stations.delete()
    c = Company.objects.get(id=companyPk)
    deletedRowCountDict["Company"] = c.delete()

    return deletedRowCountDict
```