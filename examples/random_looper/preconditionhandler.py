
def get_varname():
  counter = 1
  while True:
    yield "var{}".format(counter)
    counter += 1 

def get_location(location_node):
  location_type = location_node.attrib['type']
  if location_type == 'static':
    return location_node.tag
  elif location_type == 'stack-offset':
    offset = location_node.t
    return "stack_base+{}".format(offset)

vartype_sizes = {
  'byte' : 1,
  'char' : 1,
  'float' : 4,
  'double' : 8,
  'uint32' : 4,
  'int32' : 4,
}

def get_mutable_precondition_cpp_text(config_node):
  return_text = '\n'
  vartype = conig_node.get('type')
  varsize = confg_node.get('size',1)
  varsize *= vartype_sizes[vartype]

  ptr_location = get_location(config_node.find('location'))
  return_text += "working_pointer = {};\n".format(ptr_location)
  return_text += "read(0,working_pointer,{});\n".format(varsize)

def get_precondition_cpp_text(config_node):
  condition = config_node.get('condition')
  if(condition == 'mutable'):
    return get_mutable_precondition_cpp_text(config_node)
  else
    raise NotImplemented
