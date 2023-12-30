import random

def get_int_between(start, end, prefix=''):
    def get_int():
        return prefix+str(random.randint(start, end))
    return get_int

def get_bool():
    return get_int_between(0,1)

def get_nothing():
    def f():
        return ''
    return f

def get_encoding():
    def encoding():
        return random.choice(["'UTF-8'","'UTF-16'","'UTF-16le'","'UTF-16be'"])
    return encoding

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
    'application_id': wrap_assign_method('=', get_int_between(100,1000)),
    'auto_vacuum': wrap_assign_method('=', get_int_between(0,2)),
    'automatic_index': wrap_assign_method('=', get_int_between(0,2)),
    'busy_timeout': wrap_assign_method('=', get_int_between(1000,3000)),
    'cache_size': wrap_assign_method('=', get_int_between(1500,2500, prefix='-')),
    'cache_spill': wrap_assign_method('=', get_int_between(0,1)),
    'case_sensitive_like': wrap_assign_method('=', get_int_between(0,1)),
    'cell_size_check': wrap_assign_method('=', get_int_between(0,1)),
    'checkpoint_fullfsync': wrap_assign_method('=', get_int_between(0,1)),
    'collation_list': get_nothing(),
    'compile_options': get_nothing(),
    'count_changes': wrap_assign_method('=', get_int_between(0,1)),
    'data_version': get_nothing(),
    'database_list': get_nothing(),
    'defer_foreign_keys': wrap_assign_method('=', get_int_between(0,1)),
    'encoding': wrap_assign_method('=', get_encoding()),
    'foreign_key_check': get_nothing(),
    'foreign_keys': wrap_assign_method('=', get_int_between(0,1)),
    'freelist_count': get_nothing(),
    'full_column_names': get_nothing(),
    'fullfsync': wrap_assign_method('=', get_int_between(0,1)),
    'function_list': get_nothing(),
    'ignore_check_constraints': wrap_assign_method('=', get_int_between(0,1)),
    'legacy_file_format': get_nothing(),

}

if __name__=='__main__':
    print(pragmas['analysis_limit']())