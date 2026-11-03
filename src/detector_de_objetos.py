import cv2
from ultralytics import YOLO

#Carrega o modelo YOLO
modelo = YOLO("yolo11n.pt")

#Habilita o uso da camera
cap = cv2.VideoCapture(0)

print("Iniciando detector de objetos.")

#Tradução dos objetos que queremos identificar
traducoes = {
    "bottle": "Garrafa",
    "cell phone": "Celular",
    "mouse": "Mouse",
    "keyboard": "Teclado",
    "laptop": "Notebook",
    "cup": "Copo",
    "book": "Livro",
    "chair": "Cadeira",
    "backpack": "Mochila",
    "remote": "Controle",
    "tv": "Televisao"
}

while True:
    ret, frame = cap.read()

    if not ret:
        print("Erro ao acessar a camera.")
        break

    #Espelha a imagem da camera
    frame = cv2.flip(frame, 1)

    #Realiza a detecção dos objetos
    resultados = modelo(
        frame,
        verbose=False
    )

    #Percorre os resultados encontrados
    for resultado in resultados:

        #Percorre cada objeto detectado
        for box in resultado.boxes:

            #Obtem a classe do objeto
            classe_id = int(box.cls[0])

            #Obtem o nome do objeto
            nome_objeto = modelo.names[classe_id]

            #Obtem a confianca da deteccao
            confianca = float(box.conf[0])

            #Verifica se o objeto esta na nossa lista
            if nome_objeto in traducoes and confianca >= 0.50:

                #Traduz o nome do objeto
                objeto = traducoes[nome_objeto]

                #Obtem as coordenadas do objeto
                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0]
                )

                #Desenha o retangulo ao redor do objeto
                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )

                #Converte a confianca para porcentagem
                porcentagem = confianca * 100

                #Monta o texto
                texto = f"{objeto} {porcentagem:.0f}%"

                #Exibe o nome do objeto
                cv2.putText(
                    frame,
                    texto,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )

    #Exibe a imagem da camera
    cv2.imshow(
        "Detector de objetos",
        frame
    )

    #Pressione Q para encerrar
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()