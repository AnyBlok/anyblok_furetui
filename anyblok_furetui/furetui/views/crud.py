from copy import deepcopy
from anyblok_pyramid import current_blok
from anyblok_pyramid_rest_api.querystring import QueryString
from anyblok_pyramid_rest_api.crud_resource import saved_errors_in_request
from cornice import Service
import re


def parse_key_with_two_elements(filter_):
    pattern = ".*\\[(.*)\\]\\[(.*)\\]"
    return re.match(pattern, filter_).groups()


def parse_key_with_one_element(filter_):
    pattern = ".*\\[(.*)\\]"
    return re.match(pattern, filter_).groups()[0]


def deserialize_querystring(params=None):
    """
    Given a querystring parameters dict, returns a new dict that will be used
    to build query filters.
    The logic is to keep everything but transform some key, values to build
    database queries.
    Item whose key starts with 'filter[*' will be parsed to a key, operator,
    value dict (filter_by).
    Item whose key starts with 'order_by[*' will be parse to a key, operator
    dict(order_by).
    'limit' and 'offset' are kept as is.
    All other keys are added to 'filter_by' with 'eq' as default operator.

    # TODO: Use marshmallow pre-validation feature
    # TODO: Evaluate 'webargs' python module to see if it can helps

    :param params: A dict that represent a querystring (request.params)
    :type params: dict
    :return: A suitable dict for building a filtering query
    :rtype: dict
    """
    filter_by = []
    order_by = []
    tags = []
    context = {}
    limit = None
    offset = 0
    for param in params.items():
        k, v = param
        # TODO  better regex or something?
        if k.startswith("filter["):
            # Filtering (include)
            key, op = parse_key_with_two_elements(k)
            filter_by.append(dict(key=key, op=op, value=v, mode="include"))
        elif k.startswith("~filter["):
            # Filtering (exclude)
            # TODO check for errors into string pattern
            key, op = parse_key_with_two_elements(k)
            filter_by.append(dict(key=key, op=op, value=v, mode="exclude"))
        elif k.startswith("context["):
            key = parse_key_with_one_element(k)
            context[key] = v
        elif k == "tag":
            tags.append(v)
        elif k == "tags":
            tags.extend(v.split(','))
        elif k.startswith("order_by["):
            # Ordering
            op = parse_key_with_one_element(k)
            order_by.append(dict(key=v, op=op))
        elif k == 'limit':
            # TODO check to allow positive integer only if value
            limit = int(v) if v else None
        elif k == 'offset':
            # TODO check to allow positive integer only
            offset = int(v)

    return dict(filter_by=filter_by, order_by=order_by, limit=limit,
                offset=offset, tags=tags, context=context)


class FuretuiQueryString(QueryString):
    """Parse the validated querystring from the request to generate a
    SQLAlchemy query

    :param request: validated request from pyramid
    :param Model: AnyBlok Model, use to create the query
    :param adapter: Adapter to help to generate query on some filter of tags
    """
    def __init__(self, request, Model):
        self.request = request
        self.adapter = None  # TODO check model has_furetui_adapter
        self.Model = Model
        if request.params is not None:
            parsed_params = deserialize_querystring(request.params)
            self.filter_by = parsed_params.get('filter_by', [])
            self.tags = parsed_params.get('tags')
            self.order_by = parsed_params.get('order_by', [])
            self.context = parsed_params.get('context', {})
            self.limit = parsed_params.get('limit')
            if self.limit and isinstance(self.limit, str):
                self.limit = int(self.limit)

            self.offset = parsed_params.get('offset')
            if self.offset and isinstance(self.offset, str):
                self.offset = int(self.offset)

    def get_query(self):
        query = self.Model.query()
        # TODO update query in function of user
        return query


crud = Service(name='crud',
               path='/furet-ui/crud',
               description='Generic Crud',
               cors_origins=('*',),
               cors_credentials=True,
               installed_blok=current_blok())


@crud.get()
def crud_read(request):
    # check user is disconnected
    # check user has access rigth to see this resource
    registry = request.anyblok.registry
    model = request.params['model']
    Model = registry.get(model)
    fields_ = request.params['fields'].split(',')
    fields = []
    subfields = {}

    for f in fields_:
        if '.' in f:
            field, subfield = f.split('.')
            fields.append(field)
            if field not in subfields:
                subfields[field] = []

            subfields[field].append(subfield)
        else:
            fields.append(f)

    # TODO complex case of relationship
    qs = FuretuiQueryString(request, Model)
    query = qs.get_query()
    query = qs.from_filter_by(query)
    query = qs.from_tags(query)

    query2 = qs.from_order_by(query)
    query2 = qs.from_limit(query2)
    query2 = qs.from_offset(query2)

    data = []
    pks = []
    for entry in query2:
        pk = entry.to_primary_keys()
        pks.append(pk)
        data.append({
            'type': 'UPDATE_DATA',
            'model': model,
            'pk': pk,
            'data': entry.to_dict(*fields),
        })
        for field, subfield in subfields.items():
            entry_ = getattr(entry, field)
            data.append({
                'type': 'UPDATE_DATA',
                'model': entry_.__registry_name__,
                'pk': entry_.to_primary_keys(),
                'data': entry_.to_dict(*subfield),
            })

    return {
        'pks': pks,
        'total': query.count(),
        'data': data,
    }


def create_data(registry, model, changes, uuid):
    Model = registry.get(model)
    fd = Model.fields_description()
    data = changes[model]['new'].pop(uuid, {})
    for field in data:
        if fd[field]['type'] in ('Many2One', 'One2One'):
            M2 = registry.get(fd[field]['model'])
            data[field] = M2.from_primary_keys(**data[field])

        # TODO one2many and many2many

    return Model.insert(**data)


@crud.post()
def crud_create(request):
    registry = request.anyblok.registry
    data = request.json_body
    model = data['model']
    uuid = data['uuid']
    changes = deepcopy(data['changes'])

    with saved_errors_in_request(request):
        obj = create_data(registry, model, changes, uuid)
        # create_or_update(registry, changes, firstmodel=model)
        return {
            'pks': obj.to_primary_keys(),
        }
