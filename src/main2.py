from pathlib import Path
from DataReader.data_reader_task_versioning import DataReaderTaskVersioning
from parsers.xml_ch3_parser import build_ch3_xml
from DocGen.doc_ch3_render import render_ch3_from_xml

imgconf = Path("C:\\Users\\cpisa\\Desktop\\stream\\DEVRASTA\\NSPC\\Imgconf.ini")

reader = DataReaderTaskVersioning(imgconf)
tasks = reader.read_tasks()

xml_out = Path("out/ch3.xml")
doc_out = Path("out/ch3.docx")

build_ch3_xml(tasks, xml_out)
render_ch3_from_xml(xml_out, doc_out)

print("Capitolo 3 generato correttamente")
