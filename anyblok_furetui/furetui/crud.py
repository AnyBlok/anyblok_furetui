from anyblok.declarations import Declarations
from sqlalchemy.orm import load_only, joinedload, subqueryload
from anyblok_pyramid_rest_api.querystring import QueryString
import re
import json


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
            key = parse_key_with_one_element(k)
            order_by.append(dict(key=key, op=v))
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
        self.adapter = Model.get_furetui_adapter()
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


@Declarations.register(Declarations.Model.FuretUI)
class CRUD:

    @classmethod
    def parse_fields(cls, qs_fields):
        """Prepare fields for different use cases

        returns:
        """
        fields = []
        fields2read = []
        subfields = {}

        for f in qs_fields.split(','):
            if '.' in f:
                field, subfield = f.split('.')
                fields.append(field)
                if field not in subfields:
                    subfields[field] = []

                subfields[field].append(subfield)
            else:
                fields2read.append(f)
                fields.append(f)
        fields = list(set(fields))
        return fields, fields2read, subfields

    @classmethod
    def set_from_statment(cls, model, query, fields2read, subfields):
        """Limit query object to requested fields
        """
        fd = model.fields_description()
        return query.options(
            load_only(*fields2read),
            *[(subqueryload(field).load_only(*subfield)
               if fd[field]['type'] in ('One2Many', 'Many2Many')
               else joinedload(field).load_only(*subfield))
              for field, subfield in subfields.items()]
        )

    @classmethod
    def read(cls, request):
        # check user is disconnected
        # check user has access rigth to see this resource
        model = request.params['model']
        Model = cls.registry.get(model)
        fd = Model.fields_description()

        fields, fields2read, subfields = cls.parse_fields(
            request.params['fields']
        )

        # TODO complex case of relationship
        qs = FuretuiQueryString(request, Model)
        query = qs.get_query()
        query = qs.from_filter_by(query)
        query = qs.from_tags(query)

        query2 = qs.from_order_by(query)
        query2 = qs.from_limit(query2)
        query2 = qs.from_offset(query2)

        query2 = cls.set_from_statment(Model, query2, fields2read, subfields)

        data = []
        pks = []
        from pprint import pprint
        pprint(str(query2))
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
                if entry_:
                    if fd[field]['type'] in ('Many2One', 'One2One'):
                        data.append({
                            'type': 'UPDATE_DATA',
                            'model': fd[field]['model'],
                            'pk': entry_.to_primary_keys(),
                            'data': entry_.to_dict(*subfield),
                        })
                    else:
                        for entry__ in entry_:
                            data.append({
                                'type': 'UPDATE_DATA',
                                'model': fd[field]['model'],
                                'pk': entry__.to_primary_keys(),
                                'data': entry__.to_dict(*subfield),
                            })

        # query.count do a sub query, we do not want it, because mysql
        # has a terrible support of subqueries
        # total = query.with_entities(func.count('*')).scalar()
        total = query.count()
        return {
            'pks': pks,
            'total': total,
            'data': data,
        }

    @classmethod
    def format_data(cls, Model, data):
        fd = Model.fields_description()
        linked_data = []
        for field in data:
            if fd[field]['type'] in ('Many2One', 'One2One'):
                M2 = cls.registry.get(fd[field]['model'])
                data[field] = M2.from_primary_keys(**data[field])
            if fd[field]['type'] in ('One2Many', 'Many2Many'):
                linked_data.append({
                    "field": field,
                    "model": fd[field]['model'],
                    "data": data[field],
                    "instances": [],
                })
        # Remove x2m fields
        [data.pop(key["field"]) for key in linked_data]
        return linked_data

    @classmethod
    def create(cls, model, uuid, changes):
        return cls.create_or_update(model, {"uuid": uuid}, changes)

    @classmethod
    def create_or_update(cls, model, pks, changes):
        Model = cls.registry.get(model)
        data = {}
        new = True
        # TODO: rename uuid or document that primary key should not use
        # a field called uuid
        if "uuid" in pks.keys():
            data = changes[model]["new"].pop(pks["uuid"], {})
        else:
            new = False
            for key in changes[model].keys():
                if key != "new" and dict(json.loads(key)) == pks:
                    data = changes[model].pop(key, {})
                    break
        # TODO: not sure how to skip loops when 2 objects reference each other
        # Keep in mind in case of updatating data in depth with 2 or 3 o2m.
        # intermediate object may have no changes
        # if not data:
        #     return None
        linked_data = cls.format_data(Model, data)
        if new:
            new_obj = Model.furetui_insert(**data)
        else:
            new_obj = Model.from_primary_keys(**pks)
            new_obj.furetui_update(**data)
        cls.create_or_update_linked_data(new_obj, linked_data, changes)
        return new_obj

    @classmethod
    def create_or_update_linked_data(cls, new_obj, linked_data, changes):
        for linked_field in linked_data:
            linked_model = cls.registry.get(linked_field["model"])
            linked_model_pks = set(linked_model.get_primary_keys())
            for linked_instance in linked_field["data"]:
                state = linked_instance.get("__x2m_state", None)
                if state == "ADDED":
                    primary_key = {"uuid": linked_instance["uuid"]}
                else:
                    primary_key = {}
                    for key in linked_model_pks:
                        primary_key[key] = linked_instance[key]
                if state in ["ADDED", "UPDATED"]:
                    getattr(new_obj, linked_field["field"]).append(
                        cls.create_or_update(
                            linked_field["model"],
                            primary_key,
                            changes,
                        )
                    )
                if state in ["DELETED"]:
                    linked_model.from_primary_keys(
                        **primary_key
                    ).furetui_delete()
                if state in ["LINKED"]:
                    getattr(new_obj, linked_field["field"]).append(
                        linked_model.from_primary_keys(
                            **primary_key
                        )
                    )
                if state in ["UNLINKED"]:
                    getattr(new_obj, linked_field["field"]).remove(
                        linked_model.from_primary_keys(
                            **primary_key
                        )
                    )

    @classmethod
    def update(cls, model, pks, changes):
        return cls.create_or_update(model, pks, changes)

    @classmethod
    def delete(cls, model, pks):
        Model = cls.registry.get(model)
        obj = Model.from_primary_keys(**pks)
        obj.furetui_delete()
