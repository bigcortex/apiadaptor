import json, urllib2

class ApiResource(object):
    """
    Wrapper to access django-tastyie api. Only supports Read
    Arguments:
        resource_uri: resource location
        
    Usage
    
    .. code-block:: python
    
    api = Api('http://www.used123.ca/api/v1/articles/')
    api.get_objects()
    
    
    #advanced usage
    api.add_param("language=en")
    api.add_param("published=true")
    api.load()
    
    #by default it will return 20 articles
    api.add_param("limit=5")
    api.get_objects()
    api.next() #5 next objects
    api.get_objects()
    
    """
    def __init__(self, resource_uri):
        self._resource_uri = resource_uri
        parts = resource_uri.split("/api")
        self._base_uri = parts[0]
        self._params = []
        self._meta = {}
        self._objects = []
        self._loaded = False
        
    def add_param(self, p):
        self._params.append(p)
    
    def _open_uri(self, uri):
        try:
            return json.load(urllib2.urlopen(uri))
        except urllib2.URLError, ValueError:
            return {}
            
    def load(self, uri=None):
        if not uri:
            uri = self._resource_uri + "?" + "&".join(self._params)
        else:
            uri = self._base_uri + uri
            
        results = self._open_uri(uri)
        self._objects = results.get('objects')
        self._meta = results.get('meta')
        self._loaded = True
        
    @property    
    def meta(self):
        if not self._loaded:
            self.load()
        return self._meta
    
    @property
    def objects(self):
        if not self._loaded:
            self.load()
        return self._objects
        
    def next(self):
        if self._meta and self._meta.get('next'):
            self.load(self._meta.get('next'))
            return True
        else:
            return False
    
    def previous(self):
        if self._meta and self._meta.get('previous'):
            self.load(self._meta.get('previous'))
            return True
        else:
            return False
            
    def count(self):
        return self._meta and self._meta.get('total_count') or 0
        
    def get_object(self, uri):
        uri = self._base_uri + uri
        return self._open_uri(uri)
        
        
class Api(object):
    def __init__(self, api_uri):
        try:
            self.schemas = json.load(urllib2.urlopen(api_uri))
        except urllib2.URLError, ValueError:
            self.schemas = {}
        uri_parts = api_uri.split("/api")
        self._base_uri = uri_parts[0]
        
        for schema_name, schema in self.schemas.items():
            resource_uri = self._base_uri + schema.get('list_endpoint')
            resource = ApiResource(resource_uri)
            setattr(self, schema_name, resource)

