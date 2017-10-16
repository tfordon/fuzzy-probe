from shutil import copyfile
import errno
import os
import string


_new_main_text = '''
#include <unistd.h>

void *section_start = $section_start;
void *esp, *ebp;
$static_vars

int new_main(int argc, char **argv){
  //adjust stack before setting pre-conditions
  asm("mov ebp, esp");
  asm("sub esp, $stack_size");
  
  //determine where the stack and frame pointer are
  asm("mov %esp, esp");
  asm("mov %ebp, ebp");

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
        self.stack_size = 20
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
                stack_size = self.stack_size,
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
        """instrument a binary and a default input file

        This method injects new code into a binary based on the function calls so far

        Parameters
        ----------
        folder_name : str
            Where the new binary should be placed
        modified_file_name : str
            The name of the new binary
        """

        try:
            os.makedirs(folder_name + '/testcase_dir')
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(folder_name):
                pass
            else:
                raise

        path_to_new_binary = folder_name + '/' + modified_file_name
        copyfile(self.path_to_binary, path_to_new_binary)
        self._create_cpp_file()
        self._compile_cpp_file()
        self._inject_object_into_binary(path_to_new_binary)
        self._inject_end_jumps(path_to_new_binary)
        self._create_sample_input(folder_name + '/testcase_dir/initial')
        # self._delete_intermediate_files()
        pass

    def dynamically_allocate(self, size_in_bytes=100):
        """ dynamically allocates a new section of memory in the new binary

        At runtime, allocates a new portion of memory on the heap and returns a pointer to the area

        Parameters
        ----------
        size_in_bytes : int
            The number of bytes to allocate

        Returns
        ---------
        str
            The name of the new variable
        """
        self.var_num += 1
        var_name = 'genVar%i' % var_num
        self.static_vars += 'static char * %s;\n' % var_name
        self.pre_conditions += '    %s = malloc(%i);\n' % (var_name, size_in_bytes)
        return var_name

    def set_fixed_bytes(self, location, values):
        """sets bytes at a given location

        Parameters
        ---------
        location : str
            The location to write.  This can be a fixed location (e.g. 0x40000), or based on a variable (e.g. "esp - 0x10)
        values : bytearray
            An array of bytes to copy
        """
        if not isinstance(values, bytearray):
            raise Exception("Usage set_fixed_bytes(location(string), values(bytearray))")
        for idx, value in enumerate(values):
            self.pre_conditions += '    *(char*)(%s+%s) = %s;\n' % (location, idx, value)

    def read_raw(self, location, size_in_bytes):
        """sets bytes in a given location based on stdin

        Reads from stdin and writes to a given location

        Parameters
        ----------
        location : str
            The location to write.  This can be a fixed location (e.g. 0x40000), or based on a variable (e.g. "esp - 0x10)
        size_in_bytes : int
        """
        self.pre_conditions += '    read(STDIN_FILENO, %s, %s);\n' % (location, size_in_bytes)
        self.input_bytes += bytearray([0] * size_in_bytes)

    def set_stack_size(self, stack_size):
        self.stack_size = stack_size

    # Now some syntactic sugar to make the above methods easier

    def set_fixed_int32(self, location, value):
        self.pre_conditions += '    *(int32_t*)(%s) = %s;\n' % (location, value)

    def set_fixed_address(self, location, value):
        self.pre_conditions += '    *(void*)(%s) = %s;\n' % (location, value)

    # Not implemented yet
    def read_proto_buf(self, location, rpc_spec):
        raise NotImplemented()

