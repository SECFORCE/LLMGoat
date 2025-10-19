import xml.etree.ElementTree as ET
from PIL import Image, ExifTags

XMP_NS = {
    "rdf":  "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "dc":   "http://purl.org/dc/elements/1.1/",
    "xmp":  "http://ns.adobe.com/xap/1.0/",
    "xmpMM": "http://ns.adobe.com/xap/1.0/mm/",
    "photoshop": "http://ns.adobe.com/photoshop/1.0/",
    "tiff": "http://ns.adobe.com/tiff/1.0/",
    "exif": "http://ns.adobe.com/exif/1.0/",
    "xmpRights": "http://ns.adobe.com/xap/1.0/rights/",
    "Iptc4xmpCore": "http://iptc.org/std/Iptc4xmpCore/1.0/xmlns/",
}


def _qname_to_prefixed(qname: str) -> str:
    if not qname.startswith("{"):
        return qname
    uri, local = qname[1:].split("}", 1)
    for p, u in XMP_NS.items():
        if u == uri:
            return f"{p}:{local}"
    return local


def _text_or_none(s):
    return None if s is None else s.strip() or None


def _parse_list_container(el):
    items = []
    for li in el.findall("rdf:li", XMP_NS):
        val = _text_or_none(li.text) or li.attrib.get(f"{{{XMP_NS['rdf']}}}resource")
        if val is not None:
            items.append(val)
    return items


def _parse_property_value(prop_el):
    for kind in ("Seq", "Bag", "Alt"):
        cont = prop_el.find(f"rdf:{kind}", XMP_NS)
        if cont is not None:
            return _parse_list_container(cont)
    res = prop_el.attrib.get(f"{{{XMP_NS['rdf']}}}resource")
    if res is not None:
        return res
    txt = _text_or_none(prop_el.text)
    if txt is not None:
        return txt
    nested_desc = prop_el.find("rdf:Description", XMP_NS)
    if nested_desc is not None:
        return _parse_rdf_description(nested_desc)
    return {_qname_to_prefixed(c.tag): _text_or_none(c.text) for c in list(prop_el)}


def _parse_rdf_description(desc_el):
    d = {}
    for k, v in desc_el.attrib.items():
        d[_qname_to_prefixed(k)] = v
    for child in list(desc_el):
        d[_qname_to_prefixed(child.tag)] = _parse_property_value(child)
    return d


def parse_xmp_packet(xmp_bytes_or_str):
    if isinstance(xmp_bytes_or_str, (bytes, bytearray)):
        xmp_xml = xmp_bytes_or_str.decode("utf-8", "ignore")
    else:
        xmp_xml = str(xmp_bytes_or_str)
    root = ET.fromstring(xmp_xml)
    rdf = root if _qname_to_prefixed(root.tag) == "rdf:RDF" else root.find(".//rdf:RDF", XMP_NS)
    if rdf is None:
        return {}
    out = {}
    for desc in rdf.findall("rdf:Description", XMP_NS):
        props = _parse_rdf_description(desc)
        out.update({k: v for k, v in props.items() if v is not None})
    return out


def _decode_exif(im):
    out = {}
    try:
        exif = im.getexif()
        if exif:
            for k, v in exif.items():
                name = ExifTags.TAGS.get(k, f"ExifTag_{k}")
                if name.startswith("XP") and isinstance(v, (bytes, bytearray, tuple, list)):
                    raw = bytes(v) if not isinstance(v, (bytes, bytearray)) else v
                    try:
                        v = raw.decode("utf-16-le").rstrip("\x00")
                    except Exception:
                        pass
                out[name] = v
    except Exception:
        pass
    return out


def extract_all_png_metadata_from_image(im: Image.Image):
    info = getattr(im, "info", {}) or {}
    xmp_blob = info.get("xmp") or info.get("XML:com.adobe.xmp") or info.get("XMP")
    xmp = parse_xmp_packet(xmp_blob) if xmp_blob else {}
    exif = _decode_exif(im)
    png_text = {k: v for k, v in info.items()
                if isinstance(k, str) and k not in ("xmp", "XMP", "XML:com.adobe.xmp")}
    return {"xmp": xmp, "exif": exif, "png_text": png_text}
