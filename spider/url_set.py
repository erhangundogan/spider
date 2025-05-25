import json

class URL_Set_Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, URL_Set):
            return list(obj)
        return super().default(obj)

class URL_Set:
    def __init__(self, lst: list | set | None = None):
        # generate set of urls
        self.url_set = set()
        if lst is None:
            return

        if isinstance(lst, list):
            for url in lst:
                self.add(url)
        elif isinstance(lst, set):
            self.url_set = lst
        else:
            raise TypeError("Expected a list or set of URLs")

    def add(self, url):
        # params and query strings will generate new urls
        if url.endswith('/'):
            url = url[:-1]
            self.url_set.add(url)
        elif url.endswith('index.html'):
            url = url[:-11]
            self.url_set.add(url)
        elif url.endswith('index.htm'):
            url = url[:-10]
            self.url_set.add(url)
        else:
            self.url_set.add(url)

    def remove(self, url):
        self.url_set.remove(url)

    def clear(self):
        self.url_set.clear()

    def contains(self, url):
        return url in self.url_set
    
    def __iter__(self):
        return iter(self.url_set)
    
    def __len__(self):
        return len(self.url_set)
    
    def __repr__(self):
        return f"URL_Set({self.url_set})"
    
    def __del__(self):
        # clear the set when the object is deleted
        self.url_set.clear()
