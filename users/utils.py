import os


def profile_directory_path(instance: "User", filename: str) -> str:
    """Create a directory path to upload the User's Image
    :param object instance:
        The instance where the current file is being attached.
    :param str filename:
        The filename that was originally given to the file.
        This may not be taken into account when determining
        the final destination path
    :result str: Directory path.file_extension.
    """

    image_name, extension = os.path.splitteext(filename)
    name = instance.get_full_name.lower().replace(" ", "_")
    return f"profiles/{name}/{image_name}{extension}"
