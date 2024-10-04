import os
from shareplum import Site, Office365
from shareplum.site import Version

class SharePoint:
    def __init__(self):
        # Pegar as variáveis de ambiente do Streamlit
        self.USERNAME = os.getenv('SHAREPOINT_USER')
        self.PASSWORD = os.getenv('SHAREPOINT_PASSWORD')
        self.SHAREPOINT_URL = os.getenv('SHAREPOINT_URL')
        self.SHAREPOINT_SITE = os.getenv('SHAREPOINT_SITE')
        self.SHAREPOINT_DOC = os.getenv('SHAREPOINT_DOC_LIBRARY')
        self.FOLDER_NAME = os.getenv('SHAREPOINT_FOLDER_NAME')

    def auth(self):
        # Autenticação no SharePoint
        self.authcookie = Office365(self.SHAREPOINT_URL, username=self.USERNAME, password=self.PASSWORD).GetCookies()
        self.site = Site(self.SHAREPOINT_SITE, version=Version.v365, authcookie=self.authcookie)
        return self.site

    def connect_folder(self):
        # Conectar-se à pasta no SharePoint usando a variável de ambiente para o folder
        self.auth_site = self.auth()
        self.sharepoint_dir = '/'.join([self.SHAREPOINT_DOC, self.FOLDER_NAME])
        self.folder = self.auth_site.Folder(self.sharepoint_dir)
        return self.folder

    def download_file(self, file_name):
        # Baixar um arquivo do SharePoint e salvar localmente
        self._folder = self.connect_folder()
        file = self._folder.get_file(file_name)
        
        # Caminho para salvar o arquivo temporariamente
        temp_path = os.path.join("/tmp", file_name)  # Use "/tmp" para armazenar temporariamente
        
        # Salvar o arquivo localmente no caminho temporário
        with open(temp_path, 'wb') as f:
            f.write(file)
        
        return temp_path  # Retorna o caminho do arquivo baixado
