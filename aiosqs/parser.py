from typing import Optional

from lxml import etree

from aiosqs.exceptions import ErrorData, SQSErrorResponse


def collect_elements(root, xpath: str):
    multi_response = []
    for child in root.xpath(xpath):
        item = {}
        for elem in child:
            value = elem.text.strip()
            item[elem.tag] = value
        if item:
            multi_response.append(item)
    return multi_response


def find_request_id(root) -> Optional[str]:
    for child in root.xpath("./RequestId"):
        if value := child.text.strip():
            return value
    return None


def parse_xml_result_response(action: str, body: str):
    root = etree.fromstring(body)
    request_id = find_request_id(root=root)

    # Check for errors first
    xpath = "./Error"
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
    xpath = f"./{action}Result"
    elements = collect_elements(root=root, xpath=xpath)

    # Response is a list of objects of the same type
    if len(elements) == 1 and len(elements[0]) == 1:
        key, value = list(elements[0].items())[0]
        if value == "":
            xpath = f"{xpath}/{key}"
            return collect_elements(root=root, xpath=xpath)

    # Response is 1 object
    if len(elements) == 1:
        return elements[0]

    # No response result
    return None
