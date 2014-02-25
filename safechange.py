import os

class param_name_rollback:
    def __init__(self, prototypes):
        self.prototypes = prototypes
    def __call__(self):
        for fpath in prototypes:
            for proto in prototypes[fpath]:
                for param in proto.params:
                    param.new_name = ''
                proto.dirty = False

class const_rollback:
    def __init__(self, param, prototypes, param_idx):
        param.set_const(False)
        self.data_type = param.data_type
        self.prototypes = prototypes
        self.param_idx = param_idx
    def __call__(self):
        for fpath in self.prototypes:
            for proto in self.prototypes[fpath]:
                proto.params[param_idx].data_type = self.data_type
                proto.dirty = False

def _name_to_backup_name(fname):
    assert not fname.startswith('.')
    return '.' + fname + '.bak'

def _backup_name_to_name(fname):
    assert fname.startswith('.')
    return fname[1:].replace('.bak', '')

def _backup_or_restore_file(fpath, name_func):
    folder, fname = os.path.split(fpath)
    new_name = os.path.join(folder, name_func(fname))
    with open(fpath, 'r') as f:
        txt = f.read()
    if os.path.isfile(new_name):
        os.remove(new_name)
    with open(new_name, 'w') as f:
        f.write(txt)
        
def backup_file(fpath):
    _backup_or_restore_file(fpath, _name_to_backup_name)
    
def restore_file(fpath):
    folder, fname = os.path.split(fpath)
    fpath = os.path.join(folder, _name_to_backup_name(fname))
    _backup_or_restore_file(fpath, _backup_name_to_name)

