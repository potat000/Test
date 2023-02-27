# How to save files into database

## Settings
Set in settings.py: ```DEFAULT_FILE_STORAGE = 'evcoos.storage.EvcoFileStorage'```
EvcoFileStorage in evcoos.storage.py is a DB Storage we developed by ourselves to deal with bugs ralated to suites.
Then, add to urls.py: ```url(r'^files/', include('db_file_storage.urls')),```

## Model Fields
Every FileField requires setting a additional model which is used to access infomation of FileField. The following takes VehicleFile for example:
1. Create a VehicleFileModel to access information of FileField firstly:
   ```console
   class VehicleFileModel(models.Model):
       bytes = models.TextField()
       filename = models.CharField(max_length=255)
       mimetype = models.CharField(max_length=50)
   ```
1. Next, set upload_to in FileField. The format is [name of accessed model]\bytes\filename\mimetype:
   ```console
   class VehicleFile(BaseModel):
       description = models.TextField(default="")
       vehicleFile = models.FileField(upload_to='asset.VehicleFileModel\\bytes\\filename\\mimetype')
       asset = models.ForeignKey('Asset', on_delete=models.SET_NULL, null=True)
   ```
    
## How to read files in database

### Download
```console
<a href='{% url "db_file_storage.download_file" %}?name={{ object.vehicleFile }}'>
     <i>Click here to download the picture</i>
</a>
```

### Browse(image)
```console
<img src="{% url 'db_file_storage.get_file' %}?name={{ object.vehicleFile }}" />
```