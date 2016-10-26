from random import choice

import graphviz

from .spaces import (
    AtomicSpace,
    JoinedSpace,
    ProductSpace,
    SpaceFormattingError,
    CombinedSpace,
    Variable,
    Operator)

import logging
log = logging.getLogger(__name__)
logging.basicConfig()
log.setLevel('INFO')

def to_dot(space):
    def to_dot_recursive(space, graph):
        #print([k if type(k)==str else (type(k[1]).__name__, id(k[1])) for k in space_list.values()])
        if id(space) in space_list:
            log.error('to_dot:Recursion:%s:%s' % (type(space), type(graph)))
            raise SpaceFormattingError('Recursion occured!')

        space_list.append(space)

        if isinstance(space, AtomicSpace):
            atomic_to_dot(space, graph)
        elif isinstance(space, JoinedSpace):
            joined_to_dot(space, graph)
        elif isinstance(space, ProductSpace):
            product_to_dot(space, graph)
        else:
            raise SpaceFormattingError(
                'No dot-translation for type: %s' % type(space))

    def atomic_to_dot(space, graph):
        if type(space) == Variable:
            graph.node(
                name = 'N' + str(id(space)),
                label = str(space.name) + '=' + repr(space.domain),
                shape = 'parallelogram')
        else:
            graph.node(
                name = 'N' + str(id(space)),
                label = str(space))

    def joined_to_dot(space, graph):
        log.debug('to_dot:enter JoinedSpace')
        label_parts = []
        new_edges = []
        parent_node_id = 'N' + str(id(space))
        graph.node(parent_node_id, 'join')

        for subspace in space:

            if subspace not in space_list:
                to_dot_recursive(subspace, graph)

            if isinstance(subspace, ProductSpace):
                subnode_id = 'N' + str(id(subspace)) + ':out:s'
            else:
                subnode_id = 'N' + str(id(subspace))

            graph.edge(parent_node_id, subnode_id, arrowsize='0.7')


    def product_to_dot(space, graph):
        log.debug('to_dot:enter ProductSpace')
        label_parts = []
        new_edges = []
        parent_node_id = 'N' + str(id(space))

        for key, subspace in space.items():

            if subspace not in space_list:
                to_dot_recursive(subspace, graph)

            if isinstance(subspace, ProductSpace):
                subnode_id = 'N' + str(id(subspace)) + ':out:s'
            else:
                subnode_id = 'N' + str(id(subspace))

            cell_label = 'f' + str(id(key))

            edge_props = {'arrowsize':'0.7'}

            new_edges.append([
                ':'.join([parent_node_id, cell_label, 'n']),
                subnode_id,
                edge_props,
            ])

            if type(key) is int: key = ""#'"#'⛀'#'🌕'#'▔' # ⫰
            label_parts.append('<%s> %s' % (cell_label, key))

        if type(space) == ProductSpace:
            op_name = 'prod'
            shape = 'Mrecord'
        else:
            op_name = space.operator.name
            shape = 'record'

        label = '{{%s}|<out> %s}' % ('|'.join(label_parts), op_name)
        graph.node(parent_node_id, label, shape=shape)
        for head, tail, props in new_edges:
            graph.edge(head, tail, **props)
        #graph.edges(new_edges)

    space_list = []
    graph = graphviz.Digraph('Space') #, filename='space.gv')
    graph.body.append('rankdir=BT')
    to_dot_recursive(space, graph)

    return graph
