import os
from app.core.config import settings
from app.core.logger import logger

class StorageService:
    def __init__(self):
        self.base_path = settings.STORAGE_PATH
        self.subdirs = ["bpmn", "docx", "reports", "temp"]

    def ensure_dirs(self):
        """Cria os diretórios necessários se não existirem."""
        try:
            if not os.path.exists(self.base_path):
                os.makedirs(self.base_path)
            
            for subdir in self.subdirs:
                path = os.path.join(self.base_path, subdir)
                if not os.path.exists(path):
                    os.makedirs(path)
                    logger.info(f"Diretório criado: {path}")
        except Exception as e:
            logger.error(f"Erro ao criar diretórios de storage: {str(e)}")
            raise e