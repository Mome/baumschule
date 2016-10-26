



class A:
    def __new__(cls, arg):
        print('A.new(%s, %s)' % (cls,arg))
        return object.__new__(B)

    def __init__(self):
        print('A.init(%s)' % self)


class B(A):
    #def __new__(cls):
    #    print('B.new(%s)' % cls)
    #    return object.__new__(cls)

    def __init__(self, arg):
        print('B.init(%s, %s)' % (self,arg))

a = A('foo')

print(a, type(a))
