from pprint import pprint as pp
import copy
import clips


##############################################################################
#
#
# show_and_assert_fact - execute a show command, parse the show command output,
#            and assert a fact based on the output
#
# Example of parsed data from a show command created by a "genie_parser"
# This example shows state information for LISP instances.
# The data for the instance is a "sub_dictionary" contained in the "per_instance_dict"
# The genie_parser generates this dictionary structure
#
#    {'ospf_neighbor': {'3.3.3.3': {'neighbor_id': '3.3.3.3', 'interface': 'GigabitEthernet0/0/0/3'}}} 
#
# This is the FACT definition used to process the data returned by the parser
#
#   {"fact_type": "show_and_assert",
#    "device": 'XRv9K-R2',
#    "device-index": 0,
#    "access-method": "ssh",
#    "command": "sh ospf neighbor",
#    "genie_parser": "ShowOSPFNeighborXR",
#    "assert_fact_for_each_item_in": "ospf_neighbor",
#    "protofact": {"template": "ospf-neighbor-data",
#                  "slots": {"device": "device",
#                            "neighbor_id": "$+neighbor_id",
#                            "interface": "$+interface"
#                           },
#                  "types": {"device": "str",
#                            "neighbor_id": "str",
#                            "interface": "str"
#                           }                  
#                 }
#   }

#############################################################################
def test_show_and_assert_fact(env, template, fact, response):
    print("\n********** Parsed response data translated into dictionary **************")
    try:
        #
        # use the parsed output of a show command that will be in the form of a python dictionary
        # The "fact" dictionary includes a field indentifying what part of the parsed data
        # to use to generated the CLIPs FACT
        #
        parsed_genie_output = response
        sub_dictionary_list = test_find(fact["assert_fact_for_each_item_in"], parsed_genie_output)
        import copy
        #
        # If there are multiple sets of data in the parsed response, each will be in a sub_dictionary
        # A FACT is generated for each sub_dictionary
        #
        for sub_dictionary in sub_dictionary_list:
            print(f"sub_dictionary entry: {sub_dictionary}")
            #
            # Each "item" in the sub_dictionary is
            # Addeded to a dictionary in the form required to generate a CLIPs FACT
            #
            for item in sub_dictionary:
                protofact = copy.deepcopy(fact["protofact"])
                for slot in protofact["slots"]:
                    value = protofact["slots"][slot]
                    #
                    # insert the device name into the fact
                    #
                    if value == "device":
                        protofact["slots"][slot] = value.replace("device", fact["device"])
                    elif type(value) == str and "$" in value:
                        protofact["slots"][slot] = value.replace("$", item)

                test_assert_template_fact(env, template, protofact, sub_dictionary)
    except Exception as e:
        print("\n&&&& show_and_assert exception: \n" + str(e))

##############################################################################
#
# find - return nested dictionary value given a dictionary (j) and a string
#		 element (element) in the form of "Garden.Flowers.White"
#
#############################################################################
def test_find(element, j):
    try:
        if element == "":
            return j
        keys = element.split('+')
        rv = j
        for i, key in enumerate(keys):
            if key == '*':
                new_list = []
                new_keys = copy.deepcopy(keys[i + 1:])  # all the keys past the * entry
                for entry in rv:  # for each entry in the * dictionary
                    new_rv = copy.deepcopy(rv[entry])
                    for new_key in new_keys:
                        new_rv = new_rv[new_key]
                    for e in new_rv:
                        new_rv[e]["upper_value"] = entry
                    new_list.append(new_rv)
                return new_list
            else:
                # normal stepping through dictionary
                try:
                   rv = rv[key]
                except Exception as e:
                    print(">> find exception: key: ", str(e), key)
                    return
        return [rv]
    except Exception as e:
        print("\n&&&& find exception: \n", str(e), element, j)


##############################################################################
#
# test_assert_template_fact - given a protofact, assert the fact into the clips system
#
# This function generates a python dictionary from the FACT data
# The python dictionary contains all of the slots that are applied to a FACT template
# The clipspy template.assert_fact method creates a CLIPs FACT using a python dictionary produced by this function
#
#############################################################################
def test_assert_template_fact(env, template, protofact, sub_dictionary):
        try:
            template = env.find_template(protofact["template"])
            fact1 = {}
            for slot, value in protofact["slots"].items():
    #
    # If the "value" is in a subdirectory, look up the final value in the sub_dictionary
    #
                if type(value) is str and "+" in value:
                    value = test_find(value, sub_dictionary)[0]
    #
    # Use "types" in the protofact to determine the type to assert in the FACT
    #
                try:
                    if protofact["types"][slot] == "int":
                        fact1[slot] = int(value)
                    elif protofact["types"][slot] == "flt":
                        fact1[slot] = float(value)
                    else:
                        fact1[slot] = str(value).replace(" ", "_")
                except Exception as e:
                    print("\n%%%% DDR Error: Exception assert_template_fact: type error: " + str(e))
    #
    # Assert the FACT defined by a Python dictionary
    #
            try:
                template.assert_fact(**fact1)
            except Exception as e:
                print("%%%% DDR Exception: template.assert_fact: " + str(e))

        except Exception as e:
            print("\n%%%% DDR Error: Exception assert_template_fact: " + str(e))
