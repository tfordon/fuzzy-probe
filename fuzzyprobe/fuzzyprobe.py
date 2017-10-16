from shutil import copyfile
import errno
import os
import string


_new_main_text = '''
#include <unistd.h>

void *section_start = $section_start;
$static_vars

int new_main(int argc, char **argv){
  $pre_conditions

  goto *section_start;

  exit(42); //this should never get called
}  

int end_check(){
  $post_conditions
  
  exit(0);
}

'''

_elfsh_text = '''
load $binary_name
load _newMain.o

reladd 1 2
reladd 1 2

redir main new_main
save $new_binary_name

exit
'''

class Fuzzyprobe(object):
    '''
    The main instrumentation interface
    '''

    def __init__(self, path_to_binary, start_address, end_address=None):
        self.path_to_binary=path_to_binary
        self.pre_conditions = ''
        self.post_conditions = ''
        self.static_vars = ''
        self.start_address = start_address
        self.end_addresses = []
        self.var_num = 0
        self.input_bytes = bytearray()
        if end_address is not None:
            self.end_addresses.append(end_address)

    def add_end_address(self,address):
        self.end_addresses.append(address)

    def _create_cpp_file(self):
        text = string.Template(_new_main_text)
        with open('_newMain.c', 'w') as text_file:
            text_file.write(text.substitute(
                static_vars = self.static_vars,
                section_start = self.start_address,
                pre_conditions = self.pre_conditions,
                post_conditions=self.post_conditions))

    def _compile_cpp_file(self):
        os.system('gcc -m32 -c -O0 -o _newMain.o _newMain.c')
        pass

    def _inject_object_into_binary(self, new_binary_name):
        text = string.Template(_elfsh_text)
        with open('_inject.esh', 'w') as text_file:
            text_file.write(text.substitute(binary_name=self.path_to_binary, new_binary_name=new_binary_name))
        os.system('elfsh < _inject.esh')

    def _inject_end_jumps(self, path_to_new_binary):
        radare_script = 'aa\noo+\n'
        for end_address in self.end_addresses:
            radare_script += 's %s\nwa call `afl~end_check[0]`' % end_address;
        with open('_radare_script', 'w') as text_file:
            text_file.write(radare_script)
        os.system('radare2 -q -i _radare_script w %s' % path_to_new_binary )

    def _create_sample_input(self, initial_input_path):
        with open(initial_input_path, 'wb') as input_file:
            input_file.write(self.input_bytes)

    def _delete_intermediate_files(self):
        os.remove('_newMain.c')
        os.remove('_newMain.o')
        os.remove('_inject.esh')
        os.remove('_radare_script')
        pass

    def instrument(self, folder_name="output", modified_file_name="binToTest"):

        try:
            os.makedirs(folder_name + '/testcase_dir')
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(folder_name):
                pass
            else:
                raise

        path_to_new_binary = folder_name + '/' + modified_file_name
        copyfile(self.path_to_binary, path_to_new_binary)
        # create a new binary based on the old
        # create a new object file based on pre/post conditions
        self._create_cpp_file()
        self._compile_cpp_file()
        self._inject_object_into_binary(path_to_new_binary)
        self._inject_end_jumps(path_to_new_binary)
        self._create_sample_input(folder_name + '/testcase_dir/initial')
        # self._delete_intermediate_files()
        pass

    def create_local_stack(self, frame_pointer_offset, stack_offset, total_size=2**12, readonly=False):
        if self.local_stack_created:
            raise 'Can only call create_local_stack once'
        self.local_stack_created = True

        self.pre_conditions += "void *mmap_ptr, *esp, *ebp;\n"

        if readonly:
            prot_str = "PROT_READ"
        else:
            prot_str = "PROT_READ | PROT_WRITE"

        self.pre_conditions += "mmap_ptr = mmap(0, %s, %s, MAP_PRIVATE | MAP_ANONYMOUS, -1, %s);\n" % (total_size, prot_str, total_size);
        self.pre_conditions += "mmap_ptr = mmap(0, %s, %s, MAP_PRIVATE | MAP_ANONYMOUS, -1, %s);\n" % (total_size, prot_str, total_size);

        self.pre_conditions += "esp = mmap_ptr + %s - %s;\n" % (total_size, stack_offset)
        self.pre_conditions += "ebp = mmap_ptr + %s - %s;\n" % (total_size, frame_pointer_offset)

        self.pre_conditions += "asm(\"mov esp, %esp\");\n"
        self.pre_conditions += "asm(\"mov ebp, %ebp\");\n"

        self.frame_pointer_address = 'ebp';

    def dynamically_allocate(self, size_in_bytes=100):
        self.var_num += 1
        var_name = 'genVar%i' % var_num
        self.static_vars += 'static char * %s;\n' % var_name
        self.pre_conditions += '    %s = malloc(%i);\n' % (var_name, size_in_bytes)
        return var_name

    def set_fixed_int32(self, location, value):
        self.pre_conditions += '    *(int32_t*)(%s) = %s;\n' % (location, value)

    def set_fixed_address(self, location, value):
        self.pre_conditions += '    *(void*)(%s) = %s;\n' % (location, value)

    def read_raw(self, location, size_in_bytes):
        self.pre_conditions += '    read(STDIN_FILENO, %s, %s);\n' % (location, size_in_bytes)
        self.input_bytes += bytearray([0] * size_in_bytes)
        
