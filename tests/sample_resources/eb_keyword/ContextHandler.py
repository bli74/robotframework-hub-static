import random
import re
from robot.libraries.BuiltIn import BuiltIn


class ContextHandler:
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        self.context_map = {}
        self.wsdl_info_map = {}
        self.soi_version = ''

    def set_global_context(self):
        """
        Creates a global context map to store all the place holders and its values. 
        Should be called only once per test suite. For rest and soap tests, this
        keyword is called with Init Soap Clients keyword
        Also creates other map holding all the WSDL urls for lazy initialization and
        a variable to store the soi version
        """
        self.context_map = {}
        self.wsdl_info_map = {}
        self.soi_version = BuiltIn().get_variable_value("${SOIVERSION}")

    def add_random_string_to_context(self, key, prefix=None):
        """
        Generates a random string with a prefix, when given and adds to the context with the given key
        """
        random_number = random.randint(1, 100000000)
        if prefix is None:
            generated_string = str(random_number)
        else:
            generated_string = prefix + str(random_number)

        self.context_map[key] = generated_string
        return generated_string

    def add_to_context(self, key, value):
        """
        Adds a value to the context within the given key
        """
        self.context_map[key] = value
        return value

    def get_context_variable_by_key(self, key):
        """
        Returns the value of a variable for the given key
        """
        if key in self.context_map:
            return self.context_map[key]
        return "null"

    def clean_up_context(self):
        """
        Clean up the context map
        """
        self.context_map.clear()

    def replace_input_placeholders_from_context(self, request):
        """
        Replaces all place holders from the request input file with the values of the variables in the context:
        
        In the input file:
        <Username>userNameHolder</Username>
        
        In the context map
        contextMap[userNameHolder] ->  EOC
        
        In the input file, after the method call:
        <Username>EOC</Username>
        """
        for key in self.context_map:
            request = re.sub(r"(?<=[\W])" + key + r"(?=[\W])", self.context_map[key], request)

        """
        once all holders are replaced, we replace the soiVersionHolder for the common commands from requestLib
        """
        request = request.replace("soiVersionHolder", self.soi_version)
        return request

    def set_up_soi_version(self, soi_version):
        """
        Sets up the soi version in the global variable
        """
        self.soi_version = soi_version
