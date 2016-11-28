
c.add_subgroup('display_dot')
c.display_dot.apply_symbol = '@'


color_schemes = {
    'light' : {
        'apply' : 'lightblue',
        'background' : 'white',
        'border' : 'white',
        'combination' : '#ffc65d',
        'edge' : '#404040',
        'font' : '#404040',
        'operation' : 'lightgreen',
        'primitive' : '#f16745',
        'value' : '#93648d',
    },
    'dark' : {
        'apply' : '#4cc3d9',
        'background' : '#404040',
        'border' : '#404040',
        'combination' : '#ffc65d',
        'edge' : 'white',
        'font' : 'white',
        'operation' : '#7bc8a4',
        'primitive' : '#f16745',
        'value' : '#93648d',
    },
    'dark2' : {
        'apply' : '#006699',
        'background' : '#333333',
        'border' : 'white',
        'combination' : '#EE9911',
        'edge' : 'white',
        'font' : 'white',
        'operation' : '#009966',
        'primitive' : '#ae1414',
        'value' : '#93648d',
    },
}

c.display_dot.colors = type(c).from_dict(color_schemes)
