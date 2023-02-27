from utils.services.customid import CustomIdService,ContextService

## create context
from task.models import TaskEntity
from customer.models import Company

anyCompany = Company.objects.get(pk=1) # vera's company: "123"
context = ContextService.getOrCreateFromModelAndCompany(TaskEntity,anyCompany)

## create CustomId entry for the context 
## TODO: companies can define their own templates themselves in a form when creating the first record of models in CPortal views
label = 'test-label'
padWidth = 12
idStart = 1
template = CustomIdService.generateSimpleTemplate('testPrefix-','optionalTestSuffix')
createdBy = 'test'
CustomIdService.create(context,'test-label',padWidth,idStart,template,createdBy)