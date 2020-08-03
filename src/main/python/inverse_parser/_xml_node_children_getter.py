# Copyright (c) Aniskov N.


class _XmlNodeChildrenGetter:
    @staticmethod
    def get_children(xml_node, with_tag=None):
        if with_tag:
            return xml_node.findall(with_tag)

        return xml_node.findall('*')

    @staticmethod
    def get_unique_child(xml_node, with_tag=None):
        if with_tag:
            res = xml_node.findall(with_tag)
        else:
            res = xml_node.findall('*')

        if not res:
            return None
        if len(res) > 1:
            raise RuntimeError(f'{len(res)} children of {xml_node.tag} with tag={with_tag} found.'
                               f' But {with_tag} expected to be unique')
        else:
            return res[0]
