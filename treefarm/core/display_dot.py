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
    _to_dot_recursive(param, graph, recursion_tracker=[])
    return graph

def _to_dot_recursive(param, graph, recursion_tracker):
    assert param not in recursion_tracker, \
        'Recursion:%s:%s' % (type(param), type(graph))

    if isinstance(param, Primitive):
        print('0')
        _primitive_to_dot(param, graph)
    elif _gets_record_shape(param):
        print('1')
        _paint_record(param, graph, recursion_tracker)
    elif not isinstance(param, Parameter):
        print('2')
        _value_to_dot(param, graph)
    else:
        print('3')
        _paint_associative_node(param, graph, recursion_tracker)

def _primitive_to_dot(param, graph):
    graph.node(
        name = 'N' + str(id(param)),
        label = str(param))

def _value_to_dot(param, graph):
    graph.node(
        name = 'N' + str(id(param)),
        label = str(param),
        shape='circle')


def _paint_associative_node(param, graph, recursion_tracker):
    label_parts = []
    new_edges = []
    parent_node_id = 'N' + str(id(param))
    graph.node(parent_node_id, 'join')

    for element in param.domain:

        if element not in recursion_tracker:
            _to_dot_recursive(element, graph, recursion_tracker)

        if _gets_record_shape(element):
            subnode_id = 'N' + str(id(element)) + ':out:s'
        else:
            subnode_id = 'N' + str(id(element))

        graph.edge(parent_node_id, subnode_id, arrowsize='0.7')


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

    shape = 'record'
    op_name = param.operation.name
    label = '{{%s}|<out> %s}' % ('|'.join(label_parts), op_name)
    graph.node(parent_node_id, label, shape=shape)
    for head, tail, props in new_edges:
        graph.edge(head, tail, **props)

def _gets_record_shape(param):
    if not isinstance(param, Apply):
        return False
    return 'associative' in param.operation.properties
