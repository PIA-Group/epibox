import json
import ast


def get_default(username):

    try:
        with open(
            "/home/{}/Documents/epibox/args.json".format(username), "r"
        ) as json_file:
            defaults = json_file.read()
            defaults = ast.literal_eval(defaults)

    except Exception as e:  # the first time using EpiBOX Core, there will be no default file
        with open("./default_args.json") as d:
            defaults = json.load(d)

        with open(
            "/home/{}/Documents/epibox/args.json".format(username), "w+"
        ) as json_file:
            json.dump(defaults, json_file)

    return defaults
