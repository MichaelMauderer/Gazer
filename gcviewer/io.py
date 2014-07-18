import bson


class GCFileReader():
    def __init__(self, file):
        data = bson.loads(file.read())
        body = data['data']
        print(data)


def write_file(scene):
    wrapper = {'encoder': 'gcviwer',
               'version': '0.1',
               'compression': None,
               'type': 'simple_stack'
               }
    data = {'lookup_table': scene,
            'frames': { 'key', 'value'

            }
           }

    wrapper['data'] = data
