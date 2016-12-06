import logging

import graphviz

from .spaces import (
    Parameter,
    Operation,
    Combination,
    Primitive,
    Categorical,
    Apply)

from .environment import get_config
from .domains import Interval, ParameterList

log = logging.getLogger(__name__)
logging.basicConfig()

c = get_config().graphviz
schemes = c.colors


def todot(param, color_scheme='light'):

    global colors
    colors = schemes[color_scheme]

    graph = graphviz.Digraph('Parameter')
    graph.body.append('rankdir=BT')

    styles = {
        'graph': {
            'fontsize': '16',
            'fontcolor': colors['font'],
            'bgcolor': colors['background'],
            'rankdir': 'BT',
        },
        'nodes': {
            'fontname': 'Helvetica',
            'fontcolor': colors['font'],
            'color': colors['border'],
            'style': 'filled',
            'fillcolor': colors['apply'],
        },
        'edges': {
            'style': 'dashed',
            'color': colors['edge'],
            'arrowsize': '0.6',
            'arrowhead': 'open',
            'fontname': 'Courier',
            'fontsize': '12',
            'fontcolor': colors['font'],
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
    assert id(param) not in recursion_tracker, \
        'Recursion:%s:%s' % (type(param), type(graph))

    recursion_tracker.append(id(param))

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
    if param.symbol:
        label = param.symbol
        if type(param) is Categorical:
            shape = 'circle'
        else:
            shape = 'square'
    else:
        label = str(param.domain)
        if type(param) is Categorical:
            shape = 'oval'
        else:
            shape = 'box'

    graph.node(
        name = 'N' + str(id(param)),
        label = label,
        fillcolor=colors['primitive'],
        shape=shape)


def _value_to_dot(param, graph):
    if isinstance(param, Operation):
        color = colors['operation']
        if 'associative' in param.properties:
            if param.symbol:
                shape = 'circle'
            else:
                shape = 'oval'
        else:
            if param.symbol:
                shape = 'square'
            else:
                shape = 'box'
        label = param.symbol if param.symbol else str(param)
    else:
        color = colors['value']
        label = str(param)
        if len(label) <= 1:
            shape = 'square'
        else:
            shape = 'box'


    graph.node(
        name = 'N' + str(id(param)),
        label = label,
        fillcolor = color,
        shape = shape)


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

    if isinstance(op, Combination):
        color = colors['combination']
    else:
        color = colors['apply']

    graph.node(parent_node_id, name, shape=shape, fillcolor=color)

    for element in param.domain:

        if id(element) not in recursion_tracker:
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
        if id(element) not in recursion_tracker:
            _to_dot_recursive(element, graph, recursion_tracker)

        if _gets_record_shape(element):
            subnode_id = 'N' + str(id(element)) + ':out:s'
        else:
            subnode_id = 'N' + str(id(element))

        cell_label = 'f' + str(id(key))

        edge_props = {}

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
    if not isinstance(param.operation, Operation):
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
        if id(element) not in recursion_tracker:
            _to_dot_recursive(element, graph, recursion_tracker)

        if _gets_record_shape(element):
            subnode_id = 'N' + str(id(element)) + ':out:s'
        else:
            subnode_id = 'N' + str(id(element))

        cell_label = 'f' + str(id(key))

        edge_props = {}

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

    edge_props = {}

    new_edges.append([
        ':'.join([parent_node_id, 'op', 'w']),
        subnode_id,
        edge_props,
    ])

    label = '{{%s}|{<op> |<out> %s}}' % ('|'.join(label_parts), c.apply_symbol)
    graph.node(parent_node_id, label, shape=shape)
    for head, tail, props in new_edges:
        graph.edge(head, tail, **props)
