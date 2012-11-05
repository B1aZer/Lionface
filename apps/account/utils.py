import os


def get_thumb_name(path):
    name, ext = os.path.splitext(path)
    return name + '.thumb' + ext

