import os


def unique_path(original_path):
    if not os.path.exists(original_path):
        return original_path
    else:
        i = 1
        path = ".".join(original_path.split(".")[:-1]) + "_1." + original_path.split(".")[-1]
        while os.path.exists(path):
            i += 1
            path = ".".join(original_path.split(".")[:-1]) + "_{}.".format(i) + original_path.split(".")[-1]
        return path
