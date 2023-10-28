from file_repository import FileRepository


workspace = FileRepository("../example-big")
print(workspace.to_path_list_string(True))
print(workspace.to_path_xml_string(True))
print(workspace.to_path_list_string(False))
print(workspace.to_path_xml_string(False))