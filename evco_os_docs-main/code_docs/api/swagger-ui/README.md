# FAQs

# How can I exclude a view from the API documentation?
([it was made in DRF as an announcement](https://www.django-rest-framework.org/community/3.9-announcement/)):

> ## `exclude_from_schema`
> 
> Both `APIView.exclude_from_schema` and the `exclude_from_schema` argument to the `@api_view` have now been removed.
> 
> For `APIView` [class-based] you should instead set a `schema = None` attribute on the view class.
> 
> For function-based views the `@schema` decorator can be used to exclude the view from the schema, by using `@schema(None)`.