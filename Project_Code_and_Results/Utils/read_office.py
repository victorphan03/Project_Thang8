import zipfile
import xml.etree.ElementTree as ET
import sys
import os

def read_docx(path):
    try:
        with zipfile.ZipFile(path) as docx:
            xml_content = docx.read('word/document.xml')
            tree = ET.XML(xml_content)
            namespace = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            paragraphs = []
            for paragraph in tree.findall('.//w:p', namespace):
                texts = [node.text for node in paragraph.findall('.//w:t', namespace) if node.text]
                if texts:
                    paragraphs.append(''.join(texts))
            return '\n'.join(paragraphs)
    except Exception as e:
        return f"Error reading docx {path}: {e}"

def read_xlsx(path):
    try:
        with zipfile.ZipFile(path) as xlsx:
            strings_xml = xlsx.read('xl/sharedStrings.xml')
            tree = ET.XML(strings_xml)
            namespace = {'x': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            strings = []
            for elem in tree.iter():
                if elem.tag.endswith('}t'):
                    if elem.text:
                        strings.append(elem.text)
            
            sheet_content = ""
            for name in xlsx.namelist():
                if name.startswith('xl/worksheets/sheet'):
                    sheet_xml = xlsx.read(name)
                    sheet_tree = ET.XML(sheet_xml)
                    for row in sheet_tree.iter():
                        if row.tag.endswith('}row'):
                            row_vals = []
                            for c in row.iter():
                                if c.tag.endswith('}c'):
                                    t = c.get('t')
                                    v = c.find('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                                    if v is None:
                                        v = c.find('.//v')
                                    if v is not None and v.text is not None:
                                        if t == 's':
                                            try:
                                                idx = int(v.text)
                                                if idx < len(strings):
                                                    row_vals.append(strings[idx])
                                            except:
                                                row_vals.append(v.text)
                                        else:
                                            row_vals.append(v.text)
                            if row_vals:
                                sheet_content += " | ".join(row_vals) + "\n"
            return sheet_content
    except Exception as e:
        return f"Error reading xlsx {path}: {e}"

def main():
    if len(sys.argv) < 3:
        print("Usage: python read_office.py <input_file> <output_file>")
        return
    path = sys.argv[1]
    out_path = sys.argv[2]
    content = ""
    if path.endswith('.docx'):
        content = read_docx(path)
    elif path.endswith('.xlsx'):
        content = read_xlsx(path)
    else:
        content = "Unsupported format"
    
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    main()
