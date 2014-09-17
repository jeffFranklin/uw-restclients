from restclients.models.r25 import Space
from restclients.r25 import nsmap, get_resource
from urllib import urlencode


def get_space_by_id(space_id):
    url = "/r25ws/servlet/wrd/run/space.xml?space_id=%s" % space_id
    return spaces_from_xml(get_resource(url))[0]


def get_spaces(**kwargs):
    """
    Return a list of reservations matching the passed filter.
    Supported kwargs are listed at
    http://knowledge25.collegenet.com/display/WSW/spaces.xml
    """
    url = "/r25ws/servlet/wrd/run/spaces.xml"
    if len(kwargs):
        url += "?%s" % urlencode(kwargs)

    return spaces_from_xml(get_resource(url))


def spaces_from_xml(tree):
    spaces = []
    for node in tree.xpath("//r25:space", namespaces=nsmap):
        space = Space()
        space.space_id = node.xpath("r25:space_id", namespaces=nsmap)[0].text
        space.name = node.xpath("r25:space_name", namespaces=nsmap)[0].text
        space.formal_name = node.xpath("r25:formal_name",
                                       namespaces=nsmap)[0].text
        spaces.append(space)

    return spaces
