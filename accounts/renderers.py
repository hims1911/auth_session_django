import json

from rest_framework import renderers


class UserRenderer(renderers.JSONRenderer):
    charset = "utf-8"
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response: json
        if "ErrorDetail" in str(data):
            response = json.dumps({"errors": data})  # if error occurred
        else:
            response = json.dumps(data)

        return response
