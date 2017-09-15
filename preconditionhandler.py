
#todo namespace

def get_varname():
  counter = 1
  while True:
    yield "var{}".format(counter)
    counter += 1 

def get_location(location_node):
  location_type = location_node.attrib['type']
  if location_type == 'static':
    return location_node.text
  elif location_type == 'stack-offset':
    offset = location_node.text
    return "&stack_base_minus13+13+({})".format(offset)

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
  vartype = config_node.get('type')
  varsize = config_node.get('size',1)
  varsize *= vartype_sizes[vartype]

  ptr_location = get_location(config_node.find('location'))
  return_text += "working_pointer = {};\n".format(ptr_location)
  return_text += "printf(\"%p\\n\", working_pointer);\n"
  return_text += "read(0,working_pointer,{});\n".format(varsize)
  return return_text

def get_precondition_cpp_text(config_node):
  condition = config_node.get('condition')
  if(condition == 'mutable'):
    return get_mutable_precondition_cpp_text(config_node)
  else:
    raise NotImplemented

def get_cpp_preconditions(config_node):
  #def get_cpp_preconditions(config_node):
  return_text = ""
  for precondition_node in config_node.findall('./pre_condition'):
    return_text += get_precondition_cpp_text(precondition_node)
    return_text += '\n'
  return return_text
 




 
