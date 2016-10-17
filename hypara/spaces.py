from containers import mixed


def prod(*args):
    list_part = []
    dict_part = {}
    for arg in args:
        if type(arg) == list:
            list_part.extend(arg)

        elif type(arg) == dict:
            if any(key in dict_part for key in arg):
                raise ParameterCombinationError("Multiple keys.")
            dict_part.update(arg)

        elif type(arg) == mixed:
            if any(key in dict_part for key in arg.kwargs):
                raise ParameterCombinationError("Multiple keys.")
            list_part.extend(arg.args)
            dict_part.update(arg.kwargs)        

    if list_part and dict_part:
        out = mixed(list_part, dict_part)
    elif list_part:
        out = list_part
    elif dict_part:
        out = dict_part
    else:
        raise ParameterInferenceError('There is no empty product.')

    return out



