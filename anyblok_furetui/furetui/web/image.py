from anyblok import Declarations
import os
import mimetypes
import base64


register = Declarations.register
Model = Declarations.Model


@register(Model.Web)
class Image:

    @classmethod
    def filepath2html(cls, filepath):
        _, fileExtension = os.path.splitext(filepath)
        mt = mimetypes.types_map[fileExtension]
        with open(filepath, 'rb') as fp:
            data_uri = base64.b64encode(fp.read()).decode('utf-8')

        return "data:%s;base64,%s" % (mt, data_uri)
