import logging

import graphviz

from .parameters import (
    Parameter,
    Operation,
    Combination,
    Primitive,
    Apply)

from .domains import Intervall, ParameterList


log = logging.getLogger(__name__)
logging.basicConfig()


def to_dot(param):
    graph = graphviz.Digraph('Parameter')
    graph.body.append('rankdir=BT')

    styles = {
        'graph': {
            'fontsize': '16',
            'fontcolor': 'white',
            'bgcolor': '#333333',
            'rankdir': 'BT',
        },
        'nodes': {
            'fontname': 'Helvetica',
            'fontcolor': 'white',
            'color': 'white',
            'style': 'filled',
            'fillcolor': '#006699',
        },
        'edges': {
            'style': 'dashed',
            'color': 'white',
            'arrowsize': '0.7',
            'arrowhead': 'open',
            'fontname': 'Courier',
            'fontsize': '12',
            'fontcolor': 'white',
        }
    }

    graph.graph_attr.update(
        ('graph' in styles and styles['graph']) or {}
    )
    graph.node_attr.update(
        ('nodes' in styles and styles['nodes']) or {}
    )
    graph.edge_attr.update(
        ('edges' in styles and styles['edges']) or {}
    )

    _to_dot_recursive(param, graph, recursion_tracker=[])

    graph.node('root', style='filled', shape='point',
        color=styles['graph']['bgcolor'], fillcolor=styles['graph']['bgcolor'])
    graph.edge('root', 'N' + str(id(param)))

    return graph

def _to_dot_recursive(param, graph, recursion_tracker):
    assert param not in recursion_tracker, \
        'Recursion:%s:%s' % (type(param), type(graph))

    if not isinstance(param, Parameter):
        _value_to_dot(param, graph)
    elif isinstance(param, Primitive):
        _primitive_to_dot(param, graph)
    elif isinstance(param.operation, Parameter):
        #if 'associative' in param.operation.operation.properties:
        # _paint_associative_record(param, graph, recursion_tracker)
        #else:
        _paint_record_composed(param, graph, recursion_tracker)
    else:
        if 'associative' in param.operation.properties:
            _paint_associative_node(param, graph, recursion_tracker)
        else:
            _paint_record(param, graph, recursion_tracker)


def _primitive_to_dot(param, graph):
    graph.node(
        name = 'N' + str(id(param)),
        label = str(param))

def _value_to_dot(param, graph):
    graph.node(
        name = 'N' + str(id(param)),
        label = param.symbol if param.symbol else str(param),
        shape = 'hexagon')


def _paint_associative_node(param, graph, recursion_tracker):
    label_parts = []
    new_edges = []
    parent_node_id = 'N' + str(id(param))

    op = param.operation
    if op.symbol:
        name = op.symbol
        shape = 'circle'
    else:
        name = op.name
        shape = 'oval'

    graph.node(parent_node_id, name, shape=shape)

    for element in param.domain:

        if element not in recursion_tracker:
            _to_dot_recursive(element, graph, recursion_tracker)

        if _gets_record_shape(element):
            subnode_id = 'N' + str(id(element)) + ':out:s'
        else:
            subnode_id = 'N' + str(id(element))

        graph.edge(parent_node_id, subnode_id)


def _paint_record(param, graph, recursion_tracker):
    label_parts = []
    new_edges = []
    parent_node_id = 'N' + str(id(param))

    for key, element in param.domain.items():

        # paint nodes of containing parameters
        if element not in recursion_tracker:
            _to_dot_recursive(element, graph, recursion_tracker)

        if _gets_record_shape(element):
            subnode_id = 'N' + str(id(element)) + ':out:s'
        else:
            subnode_id = 'N' + str(id(element))

        cell_label = 'f' + str(id(key))

        edge_props = {'arrowsize':'0.7'}

        new_edges.append([
            ':'.join([parent_node_id, cell_label, 'n']),
            subnode_id,
            edge_props,
        ])

        #if type(key) is int: key = ""#'"#'⛀'#'🌕'#'▔' # ⫰
        label_parts.append('<%s> %s' % (cell_label, key))

    op = param.operation
    if op.symbol:
        name = op.symbol
    else:
        name = op.name

    shape = 'record'
    label = '{{%s}|<out> %s}' % ('|'.join(label_parts), name)
    graph.node(parent_node_id, label, shape=shape)
    for head, tail, props in new_edges:
        graph.edge(head, tail, **props)

def _gets_record_shape(param):
    if not isinstance(param, Apply):
        return False
    return 'associative' not in param.operation.properties




# ------ Funtions for composed operations ------ #


def _paint_record_composed(param, graph, recursion_tracker):
    label_parts = []
    new_edges = []
    parent_node_id = 'N' + str(id(param))

    # paint domain
    for key, element in param.domain.items():

        # paint nodes of containing parameters
        if element not in recursion_tracker:
            _to_dot_recursive(element, graph, recursion_tracker)

        if _gets_record_shape(element):
            subnode_id = 'N' + str(id(element)) + ':out:s'
        else:
            subnode_id = 'N' + str(id(element))

        cell_label = 'f' + str(id(key))

        edge_props = {'arrowsize':'0.7'}

        new_edges.append([
            ':'.join([parent_node_id, cell_label, 'n']),
            subnode_id,
            edge_props,
        ])

        #if type(key) is int: key = ""#'"#'⛀'#'🌕'#'▔' # ⫰
        label_parts.append('<%s> %s' % (cell_label, key))

    # paint operator
    op = param.operation
    _to_dot_recursive(op, graph, recursion_tracker)
    if _gets_record_shape(element):
        subnode_id = 'N' + str(id(op)) + ':out:s'
        shape = 'record'
    else:
        subnode_id = 'N' + str(id(op))
        shape = 'Mrecord'

    edge_props = {'arrowsize':'0.7'}

    new_edges.append([
        ':'.join([parent_node_id, 'op', 'w']),
        subnode_id,
        edge_props,
    ])

    label = '{{%s}|{<op> |<out> %s}}' % ('|'.join(label_parts), 'Apply')
    graph.node(parent_node_id, label, shape=shape)

    for head, tail, props in new_edges:
        graph.edge(head, tail, **props)
