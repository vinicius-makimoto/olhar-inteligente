# Olhar Inteligente

Projeto experimental de visão computacional desenvolvido durante o curso de **Programação em IA Generativa no SENAI**. O projeto reúne protótipos em Python para cadastro e reconhecimento facial, detecção de objetos e análise visual em tempo real por webcam.

## Funcionalidades

- Aplicação web de cadastro facial com Flask: formulário para nome, e-mail, matrícula e foto; validação da imagem com DeepFace; armazenamento local em JSON e na pasta `rostos/`.
- Reconhecimento facial por webcam: compara faces com imagens cadastradas usando DeepFace e exibe estado de acesso; pode reproduzir arquivos de áudio locais.
- Detecção de olhos fechados: MediaPipe Face Landmarker e cálculo do Eye Aspect Ratio (EAR), com limiar configurado em `0.20` e alerta após `3` segundos.
- Detecção de objetos: modelo YOLO11 nano (`yolo11n.pt`) com OpenCV, câmera padrão e limiar de confiança de `50%`.
- Protótipos de análise de expressões e gênero aparente via DeepFace, além de versões anteriores marcadas com `_bk.py`.

## Tecnologias e especificações

- **Linguagem:** Python.
- **Interface web:** Flask, HTML5 e CSS.
- **Visão computacional:** OpenCV (`opencv-python`). Captura padrão pela câmera de índice `0`.
- **Análise e reconhecimento facial:** DeepFace, incluindo extração, verificação e análise de emoção/gênero aparente.
- **Detecção de objetos:** Ultralytics YOLO, configurado para carregar `yolo11n.pt`.
- **Landmarks faciais:** MediaPipe Tasks Vision, usando o asset `face_landmarker.task` no modo de vídeo.
- **Dados locais:** `cadastros.json` e fotos em `rostos/`, criados/gravados durante o uso.
- **Áudio:** `playsound` no reconhecimento facial; `winsound` no detector de olhos (Windows).
- **Dependências declaradas:** `ultralytics`, `opencv-python`, `deepface`. O detector de olhos requer também `mediapipe`; o reconhecimento com áudio requer `playsound`; a aplicação web requer `flask` (e Werkzeug, normalmente instalado como dependência do Flask). Instale dependências adicionais conforme os scripts que for executar.
- **Plataforma:** scripts de câmera e bibliotecas de IA dependem de compatibilidade com o sistema, drivers e webcam; `winsound` limita esse alerta ao Windows.

## Estrutura

```text
.
├── README.md
├── .gitignore
├── cadastros.example.json
└── src/
    ├── app.py
    ├── reconhecimento_facial.py
    ├── detector_de_olhos.py
    ├── detector_de_objetos.py
    ├── contador_de_genero.py
    ├── expressoes_bk.py
    ├── reconhecimento_facial_bk.py
    ├── requirements.txt
    ├── templates/
    └── static/
```

## Instalação

Recomenda-se Python 3.10 ou superior. Crie um ambiente virtual e instale as dependências:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r src/requirements.txt
pip install flask mediapipe playsound
```

Instale `mediapipe` e `playsound` apenas se for executar os scripts que os utilizam. Algumas bibliotecas podem exigir versões específicas ou configuração adicional conforme a versão do Python e o sistema operacional.

## Como executar

A partir da raiz do repositório:

```bash
python src/app.py
```

Acesse `http://127.0.0.1:5000/cadastro`. Para executar um experimento de câmera, rode um script por vez, por exemplo:

```bash
python src/detector_de_objetos.py
python src/detector_de_olhos.py
python src/reconhecimento_facial.py
```

É necessário permitir acesso à webcam. Para encerrar os detectores de câmera, pressione `q` na janela de vídeo.

### Modelos e arquivos locais

Os modelos e arquivos de áudio não são distribuídos neste repositório. Para os scripts correspondentes, disponibilize localmente `yolo11n.pt` e `face_landmarker.task` na pasta de execução esperada pelo código. Os scripts de reconhecimento também esperam `cadastros.json`, fotos em `rostos/` e, opcionalmente, `acesso_liberado.mp3` e `acesso_negado.mp3`. Não adicione cadastros, fotos de pessoas ou outros dados biométricos ao Git.

## Privacidade e limitações

Fotos faciais são dados biométricos e nomes, e-mails e matrículas são dados pessoais. Use dados somente com autorização e mantenha-os protegidos localmente. Este projeto é educacional/experimental; não foi preparado para controle de acesso real ou exposição pública. A aplicação original inicia o Flask com `debug=True`; desative o modo debug e implemente autenticação, proteção de dados e controles de segurança antes de qualquer implantação.

A análise de gênero aparente e emoções é uma estimativa automatizada e pode ser imprecisa. Não use essas saídas para decisões importantes sobre pessoas.

## Créditos

Desenvolvido como projeto do curso de **Programação em IA Generativa no SENAI**.
