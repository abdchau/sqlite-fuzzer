import random

def get_int_between(start, end):
    def get_int():
        return str(random.randint(start, end))
    return get_int

def get_bool():
    return get_int_between(0,1)


def wrap_assign_method(equal, fn: callable):
    def wrap_assign_method_inner():
        st = ''
        if equal == '=':
            st+='='
        else:
            st+='('

        st += str(fn())

        if equal == '=':
            pass
        else:
            st+=')'
        return st
    return wrap_assign_method_inner


pragmas = {
    'analysis_limit': wrap_assign_method('=', get_int_between(100,1000)),
}

if __name__=='__main__':
    print(pragmas['analysis_limit']())