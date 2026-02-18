import os
from app.core.config import settings
from app.core.logger import logger

class BPMNService:
    def __init__(self):
        self.output_dir = os.path.join(settings.STORAGE_PATH, "bpmn")

    async def generate_bpmn(self, process_id: str, canvas_data: dict) -> str:
        try:
            macro = canvas_data.get("macroactivities", [])
            xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" targetNamespace="http://bpmn.io/schema/bpmn">
  <bpmn:process id="Process_{process_id.replace("-","")}" isExecutable="false">
    <bpmn:startEvent id="StartEvent_1" name="Início"/>'''
            
            prev = "StartEvent_1"
            for i, act in enumerate(macro):
                tid, fid = f"Activity_{i}", f"Flow_{i}"
                xml += f'\n    <bpmn:task id="{tid}" name="{act}"/>'
                xml += f'\n    <bpmn:sequenceFlow id="{fid}" sourceRef="{prev}" targetRef="{tid}"/>'
                prev = tid

            xml += f'\n    <bpmn:endEvent id="EndEvent_1" name="Fim"/>'
            xml += f'\n    <bpmn:sequenceFlow id="Flow_End" sourceRef="{prev}" targetRef="EndEvent_1"/>'
            xml += '\n  </bpmn:process>\n</bpmn:definitions>'

            file_path = os.path.join(self.output_dir, f"{process_id}.bpmn")
            with open(file_path, "w", encoding="utf-8") as f: f.write(xml)
            return file_path
        except Exception as e:
            logger.error(f"Erro BPMN: {str(e)}")
            raise e