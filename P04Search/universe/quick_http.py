import json

from django.http import HttpResponse


class RespBuilder:
    def __init__(self, res: dict):
        self.res = res

    def build(self):
        return HttpResponse(json.dumps(self.res), content_type='application/json')