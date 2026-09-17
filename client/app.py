import os
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv
from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')
load_dotenv(Path(__file__).resolve().parent / '.env', override=True)

API_BASE_URL = os.getenv('API_BASE_URL', 'http://127.0.0.1:8000').rstrip('/')
DEFAULT_API_TOKEN = os.getenv('API_TOKEN', 'audio-demo-token')


class AudioClient(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Sistema de Processamento de Áudio')
        self.resize(980, 760)
        self.selected_path = ''
        self.history = []
        self.api_token = DEFAULT_API_TOKEN

        self.title_label = QLabel('Cliente/Servidor em Camadas para Processamento de Áudio')
        self.title_label.setStyleSheet('font-size: 16px; font-weight: bold;')

        self.path_label = QLabel('Nenhum arquivo selecionado')
        self.path_label.setStyleSheet('border: 1px solid #aaa; padding: 6px;')
        self.select_button = QPushButton('Selecionar áudio')

        self.token_label = QLabel('Token da API')
        self.token_input = QLineEdit(self.api_token)
        self.token_input.setEchoMode(QLineEdit.Password)
        self.token_input.setPlaceholderText('Token do servidor')

        self.process_combo = QComboBox()
        self.process_combo.addItems([
            'normalize', 'mono', 'speed', 'bitrate', 'format', 'original',
            'noise_reduce', 'compress', 'fade', 'trim'
        ])

        self.upload_button = QPushButton('Enviar para o servidor')
        self.upload_button.setStyleSheet('background:#2d6cdf; color:white; padding:8px;')

        self.meta_label = QLabel('Informações do arquivo:')
        self.meta_label.setStyleSheet('font-weight: bold;')

        self.now_playing_label = QLabel('Nenhum áudio em reprodução')
        self.now_playing_label.setStyleSheet('font-weight: bold; color: #1f5fbf;')

        self.original_button = QPushButton('Reproduzir original')
        self.processed_button = QPushButton('Reproduzir processado')
        self.refresh_button = QPushButton('Atualizar histórico')

        self.history_list = QListWidget()

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.8)

        form = QFormLayout()
        form.addRow('Arquivo selecionado:', self.path_label)
        form.addRow('Token:', self.token_input)
        form.addRow('Processamento:', self.process_combo)

        buttons = QHBoxLayout()
        buttons.addWidget(self.select_button)
        buttons.addWidget(self.upload_button)

        actions = QHBoxLayout()
        actions.addWidget(self.original_button)
        actions.addWidget(self.processed_button)
        actions.addWidget(self.refresh_button)

        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addLayout(form)
        layout.addLayout(buttons)
        layout.addWidget(self.meta_label)
        layout.addWidget(self.now_playing_label)
        layout.addLayout(actions)
        layout.addWidget(self.history_list)
        self.setLayout(layout)

        self.select_button.clicked.connect(self.select_file)
        self.upload_button.clicked.connect(self.upload_file)
        self.original_button.clicked.connect(self.play_original)
        self.processed_button.clicked.connect(self.play_processed)
        self.refresh_button.clicked.connect(self.load_history)
        self.token_input.editingFinished.connect(self.update_token)

        self.load_history()

    def update_token(self):
        self.api_token = self.token_input.text().strip() or DEFAULT_API_TOKEN

    def _headers(self):
        if not self.api_token:
            return {}
        return {'Authorization': f'Bearer {self.api_token}'}

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Selecionar arquivo de áudio',
            '',
            'Arquivos de áudio (*.wav *.mp3 *.ogg *.flac *.m4a *.aac *.mp4)',
        )
        if not file_path:
            return

        self.selected_path = file_path
        self.path_label.setText(Path(file_path).name)
        self.load_audio_info(file_path)

    def load_audio_info(self, file_path: str):
        import wave

        try:
            with wave.open(file_path, 'rb') as wf:
                duration = wf.getnframes() / wf.getframerate() if wf.getframerate() else 0
                info = (
                    f'Arquivo: {Path(file_path).name} | '
                    f'Tamanho: {Path(file_path).stat().st_size} bytes | '
                    f'Duração: {duration:.2f}s | '
                    f'Formato: {wf.getsampwidth() * 8}-bit | '
                    f'Canais: {wf.getnchannels()} | '
                    f'Taxa: {wf.getframerate()} Hz'
                )
            self.meta_label.setText(info)
        except Exception:
            self.meta_label.setText(
                f'Arquivo: {Path(file_path).name} | '
                f'Tamanho: {Path(file_path).stat().st_size} bytes | '
                'Não foi possível detalhar o áudio localmente.'
            )

    def upload_file(self):
        if not self.selected_path:
            QMessageBox.warning(self, 'Aviso', 'Selecione um arquivo de áudio antes de enviar.')
            return

        processing = self.process_combo.currentText()
        try:
            with open(self.selected_path, 'rb') as f:
                files = {'file': (Path(self.selected_path).name, f, 'application/octet-stream')}
                data = {'processing_type': processing}
                response = requests.post(
                    f'{API_BASE_URL}/api/upload', files=files, data=data, headers=self._headers(), timeout=120
                )
        except requests.RequestException as exc:
            QMessageBox.critical(self, 'Erro de rede', f'Não foi possível enviar o arquivo: {exc}')
            return

        if response.status_code != 200:
            QMessageBox.critical(self, 'Erro do servidor', response.text)
            return

        self.load_history()
        QMessageBox.information(self, 'Sucesso', 'Arquivo enviado e processado com sucesso!')

    def load_history(self):
        try:
            response = requests.get(f'{API_BASE_URL}/api/audios', headers=self._headers(), timeout=30)
            response.raise_for_status()
            self.history = response.json()
            self.history_list.clear()
            for item in self.history:
                label = f"{item['original_name']} | {item['processing_type']} | {item['created_at']}"
                self.history_list.addItem(QListWidgetItem(label))
        except Exception as exc:
            self.history_list.clear()
            self.history_list.addItem(QListWidgetItem(f'Erro ao consultar histórico: {exc}'))

    def play_original(self):
        if not self.history:
            QMessageBox.warning(self, 'Sem histórico', 'Nenhum áudio foi enviado ainda.')
            return
        self._play_audio(self.history[0], processed=False)

    def play_processed(self):
        if not self.history:
            QMessageBox.warning(self, 'Sem histórico', 'Nenhum áudio foi enviado ainda.')
            return
        item = self.history[0]
        if not item.get('path_processed'):
            QMessageBox.information(self, 'Sem processamento', 'Este áudio não possui versão processada.')
            return
        self._play_audio(item, processed=True)

    def _play_audio(self, item, processed: bool):
        file_name = Path(item['path_processed']).name if processed else Path(item['path_original']).name
        params = {'uuid': item['id'], 'token': self.api_token}
        url = f'{API_BASE_URL}/files/{file_name}?{urlencode(params)}'

        try:
            response = requests.get(url, timeout=30, stream=True)
            if response.status_code != 200:
                QMessageBox.critical(self, 'Erro de autorização', response.text)
                return

            temp_dir = Path(tempfile.gettempdir())
            local_path = temp_dir / f"{item['id']}_{file_name}"
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(8192):
                    if chunk:
                        f.write(chunk)

            self.now_playing_label.setText(f'Em reprodução: {file_name}')
            self.player.setSource(QUrl.fromLocalFile(str(local_path)))
            self.player.play()
        except Exception as exc:
            QMessageBox.critical(self, 'Erro ao reproduzir', str(exc))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AudioClient()
    window.show()
    sys.exit(app.exec())
