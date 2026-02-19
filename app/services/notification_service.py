import os
import shutil
from app.core.logger import logger
from app.core.config import settings

class NotificationService:
    def __init__(self):
        # Pasta que vai fingir ser o "Celular" do usuário
        self.emulator_path = os.path.join(settings.STORAGE_PATH, "whatsapp_emulator")
        if not os.path.exists(self.emulator_path):
            os.makedirs(self.emulator_path)
        
        self.chat_history = os.path.join(self.emulator_path, "chat_history.txt")

    async def send_whatsapp_message(self, number: str, text: str):
        """Emula o envio de uma mensagem de texto"""
        entry = f"\n[WHATSAPP PARA {number}]: {text}\n"
        
        with open(self.chat_history, "a", encoding="utf-8") as f:
            f.write(entry)
        
        logger.info(f"📱 EMULADOR: Mensagem enviada para {number}")

    async def send_whatsapp_file(self, number: str, file_path: str, caption: str):
        """Emula o envio de um arquivo (BPMN ou DOCX)"""
        if not os.path.exists(file_path):
            logger.error(f"❌ EMULADOR: Arquivo não encontrado: {file_path}")
            return

        file_name = os.path.basename(file_path)
        destination = os.path.join(self.emulator_path, f"recebido_{file_name}")

        # Simula o recebimento do arquivo copiando-o para a pasta do emulador
        shutil.copy(file_path, destination)

        # Registra no histórico de chat
        entry = f"\n[WHATSAPP PARA {number}]: {caption} (Arquivo: {file_name} recebido!)\n"
        with open(self.chat_history, "a", encoding="utf-8") as f:
            f.write(entry)

        logger.info(f"📁 EMULADOR: Arquivo {file_name} enviado para {number}")

    async def notify_completion(self, process_id: str, owner_email: str):
        """Simula a notificação final do sistema"""
        msg = f"Olá! O mapeamento do processo {process_id} foi concluído e os arquivos já estão disponíveis."
        await self.send_whatsapp_message("5500000000000", msg)
        return True