from copy import deepcopy

from anyblok.declarations import Declarations
from sqlalchemy.orm import load_only, joinedload, subqueryload
from anyblok_pyramid_rest_api.querystring import QueryString
import json


@Declarations.register(Declarations.Model.FuretUI)
class CRUD:

    @classmethod
    def parse_fields(cls, qs_fields, model):
        """Prepare fields for different use cases

        returns:
        """
        def add_field(data, field, model):
            f = field.split(".", 1)
            fd = cls.registry.get(model).fields_description()
            if len(f) == 1:
                if fd[field]['type'] not in ('Function', 'Many2One', 'One2One',
                                             'One2Many', 'Many2Many'):
                    data["__fields"].append(f[0])
            else:
                if f[0] not in data:
                    data[f[0]] = {"__fields": []}
                add_field(data[f[0]], f[1], fd[f[0]]['model'])

        fields = {"__fields": []}
        for field in qs_fields.split(','):
            add_field(fields, field, model)
        return fields

    @classmethod
    def add_options(cls, fields, model_name):
        """Limit query object to requested fields on any joins
        """
        model = cls.registry.get(model_name)
        fd = model.fields_description()
        load = load_only(*fields.pop("__fields"))
        joins = []
        for field, data in fields.items():
            load_method = joinedload
            if fd[field]['type'] in ('One2Many', 'Many2Many'):
                load_method = subqueryload
            joins.append(
                load_method(field).options(
                    *cls.add_options(data, fd[field]["model"])
                )
            )
        return [load, *joins]

    @classmethod
    def read(cls, request):
        # check user is disconnected
        # check user has access rigth to see this resource
        model = request.params['context[model]']
        fields = cls.parse_fields(request.params['context[fields]'], model)

        # TODO complex case of relationship
        qs = QueryString(request, cls.registry.get(model))
        query = qs.Model.query()
        query = qs.from_filter_by(query)
        query = qs.from_tags(query)

        query2 = qs.from_order_by(query)
        query2 = qs.from_limit(query2)
        query2 = qs.from_offset(query2)

        query2 = query2.options(*cls.add_options(deepcopy(fields), model))

        data = []
        pks = []

        def append_result(fields, model_name, entry):
            model = cls.registry.get(model_name)
            fd = model.fields_description()
            current_fields = fields.pop("__fields")
            current_fields.extend(fields.keys())
            data.append({
                'type': 'UPDATE_DATA',
                'model': model_name,
                'pk': entry.to_primary_keys(),
                'data': entry.to_dict(*current_fields),
            })
            for field, subfield in fields.items():
                children_entries = getattr(entry, field)
                if children_entries:
                    if fd[field]['type'] in ('Many2One', 'One2One'):
                        children_entries = [children_entries]
                    for child_entry in children_entries:
                        append_result(
                            deepcopy(fields[field]),
                            fd[field]['model'],
                            child_entry
                        )

        for entry in query2:
            pks.append(entry.to_primary_keys())
            append_result(deepcopy(fields), model, entry)

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
        if "uuid" in pks.keys() and 'uuid' not in Model.get_primary_keys():
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
                    linked_obj = linked_model.from_primary_keys(
                        **primary_key)
                    if linked_obj:
                        linked_obj.furetui_delete()
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
