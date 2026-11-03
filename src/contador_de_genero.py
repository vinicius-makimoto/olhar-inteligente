import cv2
from deepface import DeepFace

#Carrega o classificador da OpenCV
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

#Habilitar o uso da camera
cap = cv2.VideoCapture(0)

print("Iniciando modelo.")

while True:
    ret, frame = cap.read()

    if not ret:
        print("Erro ao acessar a camera.")
        break

    #Espelhar a imagem
    frame = cv2.flip(frame, 1)

    #Ajusta cores das imagens para cinza
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    #Realiza detecção de rosto
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=4
    )

    #Contadores das pessoas atualmente exibidas na camera
    homens = 0
    mulheres = 0

    for (x, y, w, h) in faces:

        #Cria retangulo ao redor do rosto
        cv2.rectangle(
            frame,
            (x, y),
            (x+w, y+h),
            (0, 255, 0),
            2
        )

        #Recorta o rosto detectado
        roi_color = frame[y:y+h, x:x+w]

        try:

            #Analisa a emoção e o genero aparente do rosto
            analysis = DeepFace.analyze(
                roi_color,
                actions=['emotion', 'gender'],
                enforce_detection=False,
                detector_backend='opencv'
            )

            #Obtem a emoção predominante
            dominant_emotion = analysis[0]['dominant_emotion']

            #Obtem o genero aparente predominante
            dominant_gender = analysis[0]['dominant_gender']

            #Tradução das emoções
            traducoes = {
                'angry': 'Raiva',
                'disgust': 'Nojo',
                'fear': 'Medo',
                'happy': 'Feliz',
                'sad': 'Triste',
                'surprise': 'Surpresa',
                'neutral': 'Neutro'
            }

            #Traduz a emoção
            emocao = traducoes.get(
                dominant_emotion,
                dominant_emotion
            )

            #Verifica a classificação de genero aparente
            if dominant_gender == 'Man':
                genero = 'Homem'
                homens += 1

            elif dominant_gender == 'Woman':
                genero = 'Mulher'
                mulheres += 1

            else:
                genero = dominant_gender

            #Monta o texto exibido acima do rosto
            texto = f"{genero} - {emocao}"

            #Exibe genero aparente e emoção
            cv2.putText(
                frame,
                texto,
                (x, y-10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

        except Exception as e:
            print("Erro ao analisar rosto:", e)

    #Exibe contador de homens
    cv2.putText(
        frame,
        f"Homens: {homens}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    #Exibe contador de mulheres
    cv2.putText(
        frame,
        f"Mulheres: {mulheres}",
        (20, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    #Exibe total de pessoas detectadas
    total = homens + mulheres

    cv2.putText(q
        frame,
        f"Total: {total}",
        (20, 120),
        cv2.FONT_HERSHEY_SIMPLEX,qqqq
        (0, 255, 0),
        2
    )

    #Exibe a imagem da camera
    cv2.imshow('Detector de emocoes', frame)

    #Pressione Q para encerrar
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()