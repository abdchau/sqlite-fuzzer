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

def get_underscore():
    def underscore():
        return '___'
    return underscore

def get_journal_mode():
    def journal_mode():
        return random.choice(['DELETE', 'TRUNCATE', 'PERSIST', 'MEMORY', 'WAL', 'OFF'])
    return journal_mode

def get_locking_mode():
    def locking_mode():
        return random.choice(['NORMAL', 'EXCLUSIVE'])
    return locking_mode


def get_wal_checkpoint():
    def wal_checkpoint():
        return random.choice(['PASSIVE','FULL','RESTART','TRUNCATE'])
    return wal_checkpoint


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

pragmas_that_need_schemas = ['application_id', 'auto_vacuum', 'cache_size', 'data_version', 'default_cache_size', 'foreign_key_check',
                             'freelist_count', 'incremental_vacuum', 'index_info', 'index_list', 'index_xinfo', 'integrity_check',
                             'journal_mode', 'journal_size_limit', 'locking_mode', 'max_page_count', 'mmap_size', 'page_count', 'quick_check',
                             'secure_delete', 'synchronous', 'table_info']

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
    'incremental_vacuum': wrap_assign_method('()', get_int_between(1,3)),
    'index_info': wrap_assign_method('()', get_underscore()),
    'index_list': wrap_assign_method('()', get_underscore()),
    'index_xinfo': wrap_assign_method('()', get_underscore()),
    'integrity_check': wrap_assign_method('()', get_underscore()),
    'journal_mode': wrap_assign_method('=', get_journal_mode()),
    'legacy_file_format': get_nothing(),
    'journal_size_limit': wrap_assign_method('=', get_int_between(10,30)),
    'locking_mode': wrap_assign_method('=', get_locking_mode()),
    'max_page_count': wrap_assign_method('=', get_int_between(1,300)),
    'mmap_size': wrap_assign_method('=', get_int_between(1,300)),
    'module_list': get_nothing(),
    'optimize': get_nothing(),
    'page_count': get_nothing(),
    'page_size': wrap_assign_method('=', get_int_between(1024,1024)),
    'parser_trace': wrap_assign_method('=', get_int_between(0,1)),
    'pragma_list': get_nothing(),
    'query_only': wrap_assign_method('=', get_int_between(0,1)),
    'quick_check': wrap_assign_method('()', get_underscore()),
    'read_uncommitted': wrap_assign_method('=', get_int_between(0,1)),
    'recursive_triggers': wrap_assign_method('=', get_int_between(0,1)),
    'reverse_unordered_selects': wrap_assign_method('=', get_int_between(0,1)),
    'secure_delete': wrap_assign_method('=', get_int_between(0,1)),
    'shrink_memory': get_nothing(),
    'soft_heap_limit': wrap_assign_method('=', get_int_between(10,50)),
    'stats': get_nothing(),
    'synchronous': wrap_assign_method('=', get_int_between(0,3)),
    'table_info': wrap_assign_method('()', get_underscore()),
    'table_list': wrap_assign_method('()', get_underscore()),
    'table_xinfo': wrap_assign_method('()', get_underscore()),
    'temp_store': wrap_assign_method('=', get_int_between(0,2)),
    'threads': wrap_assign_method('=', get_int_between(1,3)),
    'trusted_schema': wrap_assign_method('=', get_int_between(0,1)),
    'user_version': get_nothing(),
    'wal_autocheckpoint': get_nothing(),
    'wal_checkpoint': wrap_assign_method('()', get_wal_checkpoint()),
    'writable_schema': wrap_assign_method('=', get_int_between(0,1)),
}

if __name__=='__main__':
    print(pragmas['analysis_limit']())