import re

const_prefix_pat = re.compile('^const ([a-zA-Z0-9_]+)(.*)$')
   
def _squeeze(txt):
    '''Replace all runs of whitepace with a single space, and trim front and back.'''
    txt = txt.strip().replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')
    while txt.find('  ') > -1:
        txt = txt.replace('  ', ' ')
    return txt
    
def normalize_type(typ):
    '''
    Put the type portion of a parameter declaration into normalized
    form so it can be compared reliably:
    
      const char* --> char const *
      mjob_t  & --> mjob_t &
    '''
    typ = _squeeze(typ.replace('*', ' * ').replace('&', ' & '))
    m = const_prefix_pat.match(typ)
    if m:
        typ = '%s const%s' % (m.group(1), m.group(2))
    return typ

class Param:
    def __init__(self, begin, decl):
        self.begin = begin
        self.decl = decl
        self.array_spec = ''
        self.data_type = None
        self.name = None
        self.new_name = None
        self._parse()

    def is_const_candidate(self):
        dt = self.data_type
        i = dt.find('*')
        j = dt.find('&')
        # Params that are not pointers or references are passed by value,
        # so their constness is irrelevant.
        if i == -1 and j == -1:
            return False
        # Params that are *& are virtually guaranteed to be OUT params,
        # so their constness should not be adjusted.
        if i > -1 and j > -1:
            return False
        # Same for **.
        if i > -1 and i < dt.rfind('*'): 
            return False
        return True

    def is_const(self):
        return 'const' in self.decl

    def get_pivot_point(self):
        i = self.data_type.find('*')
        j = self.data_type.find('&')
        if i > -1:
            if j > -1:
                return min(i, j)
            return i
        elif j > -1:
            return j

    def set_const(self, value):
        i = self.get_pivot_point()
        if value:
            if not self.is_const():
                self.data_type = self.data_type[:i].rstrip() + ' const ' + self.data_type[i:]
        elif self.is_const():
            self.data_type = re.sub(r'\s{2,}', ' ', self.data_type.replace('const', ''))            

    def _parse(self):
        decl = squeeze(self.decl)
        m = array_spec_pat.match(decl)
        if m:
            self.array_spec = m.group(1).replace(' ', '')
            decl = decl[0:m.start(1)]
        name_idx = -1
        if not (decl.endswith('*') or decl.endswith('&') or moab_type_pat.match(decl)):
            i = decl.rfind(' ')
            if i > -1:
                name_idx = i + 1
                while decl[name_idx] == '*' or decl[name_idx] == '&':
                    name_idx += 1
                name = decl[name_idx:]
                if name in datatype_names:
                    name_idx = -1
        if name_idx > -1:
            self.data_type = decl[0:name_idx].rstrip()
            self.name = decl[name_idx:]
        else:
            self.data_type = decl
        self.data_type = normalize_type(self.data_type)

    def __str__(self):
        if self.new_name:
            return self.data_type + ' ' + self.new_name + self.array_spec
        if self.name:
            return self.data_type + ' ' + self.name + self.array_spec
        elif self.array_spec:
            return self.data_type + self.array_spec
        else:
            return self.data_type

