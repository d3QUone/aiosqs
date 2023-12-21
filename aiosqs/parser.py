import re
from logging import getLogger
from typing import Optional

from lxml import etree

from aiosqs.exceptions import ErrorData, SQSErrorResponse
from aiosqs.types import LoggerType

default_logger = getLogger(__name__)


def el_text(el) -> Optional[str]:
    if text := el.text:
        return text.strip()
    return None


def el_tag(el) -> str:
    """Returns element tag name without namespace
    {http://queue.amazonaws.com/doc/2012-11-05/}Error -> Error
    """
    tag = el.tag
    return re.sub(r"\{.*?}", "", tag, flags=re.IGNORECASE)


def collect_elements(root, xpath: str):
    multi_response = []
    for child in root.xpath(xpath):
        item = {}
        for elem in child:
            item[el_tag(elem)] = el_text(elem)
        if item:
            multi_response.append(item)
    return multi_response


def find_request_id(root) -> Optional[str]:
    for child in root.xpath("./*[local-name() = 'RequestId']"):
        if text := el_text(child):
            return text
    return None


def parse_xml_result_response(action: str, body: str, logger: Optional[LoggerType] = None):
    logger = logger or default_logger
    logger.debug("Message for %s: %s", action, body)

    parser = etree.XMLParser(
        remove_blank_text=True,
        remove_comments=True,
        remove_pis=True,
        recover=False,
    )
    root = etree.fromstring(text=body, parser=parser)

    request_id = find_request_id(root=root)

    # Check for errors first
    xpath = "./*[local-name() = 'Error']"
    if elements := collect_elements(root=root, xpath=xpath):
        error = elements[0]
        raise SQSErrorResponse(
            error=ErrorData(
                type=error["Type"],
                code=error["Code"],
                message=error["Message"],
            ),
            request_id=request_id,
        )

    # Find if it's a single element or a list
    xpath = f"./*[local-name() = '{action}Result']"
    elements = collect_elements(root=root, xpath=xpath)

    # Response is a list of objects of the same type
    if len(elements) == 1 and len(elements[0]) == 1:
        key, value = list(elements[0].items())[0]
        if not value:
            xpath = f"{xpath}/{key}"
            return collect_elements(root=root, xpath=xpath)

    # Response is 1 object
    if len(elements) == 1:
        return elements[0]

    # No response result
    return None
