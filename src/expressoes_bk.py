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

            #Analisa a emoção do rosto
            analysis = DeepFace.analyze(
                roi_color,
                actions=['emotion'],
                enforce_detection=False,
                detector_backend='opencv'
            )

            #Obtém a emoção predominante
            dominant_emotion = analysis[0]['dominant_emotion']

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

            texto = traducoes.get(
                dominant_emotion,
                dominant_emotion
            )

            #Exibe a emoção detectada
            cv2.putText(
                frame,
                texto,
                (x, y-10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 0),
                2
            )

        except Exception as e:
            print("Erro ao analisar emocao:", e)

    #Exibe a imagem da camera
    cv2.imshow('Detector de emocoes', frame)

    #Pressione Q para encerrar
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()