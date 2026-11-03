import cv2
import time
import math
import winsound
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

#Tempo necessario com os olhos fechados para emitir o alerta
TEMPO_ALERTA = 3.0

#Valor utilizado para determinar se o olho esta fechado
LIMITE_EAR = 0.20

#Caminho do modelo Face Landmarker
CAMINHO_MODELO = "face_landmarker.task"

#Configura o modelo Face Landmarker
base_options = python.BaseOptions(
    model_asset_path=CAMINHO_MODELO
)

#Configura as opcoes do detector
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_faces=1,
    min_face_detection_confidence=0.5,
    min_face_presence_confidence=0.5,
    min_tracking_confidence=0.5
)

#Cria o detector de landmarks faciais
face_landmarker = vision.FaceLandmarker.create_from_options(options)

#Pontos utilizados para calcular a abertura do olho esquerdo
OLHO_ESQUERDO = [33, 160, 158, 133, 153, 144]

#Pontos utilizados para calcular a abertura do olho direito
OLHO_DIREITO = [362, 385, 387, 263, 373, 380]

#Variavel utilizada para armazenar quando os olhos foram fechados
inicio_olhos_fechados = None

#Controla se o alerta ja foi emitido
alerta_emitido = False

#Habilita o uso da camera
cap = cv2.VideoCapture(0)

print("Iniciando detector de olhos.")
print("Pressione Q para encerrar.")

#Calcula a distancia entre dois pontos
def calcular_distancia(ponto1, ponto2):
    return math.sqrt(
        (ponto1[0] - ponto2[0]) ** 2 +
        (ponto1[1] - ponto2[1]) ** 2
    )

#Calcula o EAR do olho
def calcular_ear(landmarks, indices, largura, altura):

    #Converte os landmarks para coordenadas da imagem
    pontos = []

    for indice in indices:
        landmark = landmarks[indice]

        x = int(landmark.x * largura)
        y = int(landmark.y * altura)

        pontos.append((x, y))

    #Calcula as distancias verticais
    distancia_vertical_1 = calcular_distancia(
        pontos[1],
        pontos[5]
    )

    distancia_vertical_2 = calcular_distancia(
        pontos[2],
        pontos[4]
    )

    #Calcula a distancia horizontal
    distancia_horizontal = calcular_distancia(
        pontos[0],
        pontos[3]
    )

    #Evita divisao por zero
    if distancia_horizontal == 0:
        return 0, pontos

    #Calcula o Eye Aspect Ratio
    ear = (
        distancia_vertical_1 +
        distancia_vertical_2
    ) / (2.0 * distancia_horizontal)

    return ear, pontos

while True:

    #Captura um frame da camera
    ret, frame = cap.read()

    if not ret:
        print("Erro ao acessar a camera.")
        break

    #Espelha a imagem
    frame = cv2.flip(frame, 1)

    #Obtem tamanho da imagem
    altura, largura, _ = frame.shape

    #Converte BGR para RGB
    frame_rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    #Converte a imagem do OpenCV para MediaPipe Image
    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=frame_rgb
    )

    #Cria timestamp em milissegundos
    timestamp_ms = int(time.monotonic() * 1000)

    #Processa o rosto
    resultado = face_landmarker.detect_for_video(
        mp_image,
        timestamp_ms
    )

    #Valores iniciais
    status = "Rosto nao detectado"
    tempo_fechado = 0
    ear_medio = 0

    #Verifica se algum rosto foi detectado
    if resultado.face_landmarks:

        #Obtem os landmarks do primeiro rosto
        landmarks = resultado.face_landmarks[0]

        #Calcula EAR do olho esquerdo
        ear_esquerdo, pontos_esquerdo = calcular_ear(
            landmarks,
            OLHO_ESQUERDO,
            largura,
            altura
        )

        #Calcula EAR do olho direito
        ear_direito, pontos_direito = calcular_ear(
            landmarks,
            OLHO_DIREITO,
            largura,
            altura
        )

        #Calcula a media dos dois olhos
        ear_medio = (
            ear_esquerdo +
            ear_direito
        ) / 2.0

        #Desenha os pontos do olho esquerdo
        for ponto in pontos_esquerdo:
            cv2.circle(
                frame,
                ponto,
                2,
                (0, 255, 0),
                -1
            )

        #Desenha os pontos do olho direito
        for ponto in pontos_direito:
            cv2.circle(
                frame,
                ponto,
                2,
                (0, 255, 0),
                -1
            )

        #Verifica se os olhos estao fechados
        if ear_medio < LIMITE_EAR:

            status = "OLHOS FECHADOS"

            #Inicia o cronometro
            if inicio_olhos_fechados is None:
                inicio_olhos_fechados = time.monotonic()

            #Calcula quanto tempo os olhos estao fechados
            tempo_fechado = (
                time.monotonic() -
                inicio_olhos_fechados
            )

            #Verifica se atingiu 3 segundos
            if tempo_fechado >= TEMPO_ALERTA:

                status = "ALERTA! OLHOS FECHADOS"

                #Toca o alerta apenas uma vez
                if not alerta_emitido:

                    #Frequencia do som
                    frequencia = 2500

                    #Duracao do som em milissegundos
                    duracao = 1000

                    winsound.Beep(
                        frequencia,
                        duracao
                    )

                    alerta_emitido = True

        else:

            #Olhos estao abertos
            status = "OLHOS ABERTOS"

            #Zera o cronometro
            inicio_olhos_fechados = None

            #Permite um novo alerta
            alerta_emitido = False

    else:

        #Caso nenhum rosto seja detectado
        inicio_olhos_fechados = None
        alerta_emitido = False

    #Define a cor do status
    if status == "OLHOS ABERTOS":

        cor = (0, 255, 0)

    elif status == "OLHOS FECHADOS":

        cor = (0, 255, 255)

    elif status == "ALERTA! OLHOS FECHADOS":

        cor = (0, 0, 255)

    else:

        cor = (255, 255, 255)

    #Exibe o status
    cv2.putText(
        frame,
        f"Status: {status}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        cor,
        2
    )

    #Exibe o tempo com os olhos fechados
    cv2.putText(
        frame,
        f"Tempo: {tempo_fechado:.1f} segundos",
        (20, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        cor,
        2
    )

    #Exibe o valor EAR
    cv2.putText(
        frame,
        f"EAR: {ear_medio:.2f}",
        (20, 120),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    #Exibe uma mensagem de alerta maior
    if tempo_fechado >= TEMPO_ALERTA:

        cv2.putText(
            frame,
            "ACORDE!",
            (20, 180),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.5,
            (0, 0, 255),
            4
        )

    #Exibe a camera
    cv2.imshow(
        "Detector de Sonolencia",
        frame
    )

    #Pressione Q para encerrar
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

#Libera a camera
cap.release()

#Fecha as janelas
cv2.destroyAllWindows()

#Encerra o Face Landmarker
face_landmarker.close()