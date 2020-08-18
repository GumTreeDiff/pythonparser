# Copyright (c) Aniskov N.

import logging

from src.main.util.const import LOGGER_NAME
from src.main.util.log_util import log_and_raise_error

logger = logging.getLogger(LOGGER_NAME)


class _XmlNodeChildrenGetter:
    @staticmethod
    def get_children(xml_node, with_tag=None):
        if with_tag:
            return xml_node.findall(with_tag)

        return xml_node.findall('*')

    @staticmethod
    def get_unique_child(xml_node, with_tag=None):
        res = _XmlNodeChildrenGetter.get_children(xml_node, with_tag)
        if not res:
            return None
        if len(res) > 1:
            log_and_raise_error(f'{len(res)} children of {xml_node.tag} with tag={with_tag} found.'
                                f' But {with_tag} expected to be unique',
                                logger,
                                RuntimeError)
        else:
            return res[0]
