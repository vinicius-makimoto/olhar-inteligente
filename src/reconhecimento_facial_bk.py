import cv2
from deepface import DeepFace
import time

# 1. Carregar a "Identidade" (O Cadastramento)
# Em um sistema real, isso viria de um banco de dados.
imagem_referencia = "face_id.jpg"
print("Carregando identidade do morador...")

# Fazemos uma pré-análise para garantir que a foto de referência é válida
try:
    DeepFace.represent(
        img_path=imagem_referencia,
        model_name="VGG-Face"
    )
    print("Identidade carregada com sucesso!")

except Exception as e:
    print(f"Erro real: {e}")
    exit()

# 2. Iniciar a Câmera (A Portaria)
cap = cv2.VideoCapture(0) # Use o IP do celular aqui se preferir

print("Sistema de Portaria Ativo.")

while True:
    ret, frame = cap.read()
    if not ret: break

    # Reduzir imagem para processar rápido
    frame_small = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5) 

    # Desenhar um retângulo indicando a área de leitura
    height, width, _ = frame.shape
    cv2.rectangle(frame, (100, 100), (width-100, height-100), (255, 0, 0), 2)
    
    # 3. Verificação (Só ocorre quando aperta 'v' para não travar o vídeo)
    # Em portarias reais, isso roda automático quando um rosto para na frente da câmera
    cv2.putText(frame, "Pressione 'v' para verificar acesso", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    key = cv2.waitKey(1)
    
    if key & 0xFF == ord('v'):
        print("Verificando identidade...")
        try:           
            resultado = DeepFace.verify(
                img1_path = frame, 
                img2_path = imagem_referencia, 
                model_name = "VGG-Face",
                enforce_detection = False
            )
            
            
            if resultado['verified']:
                print(">>> ACESSO LIBERADO!" )
                cv2.rectangle(frame, (0,0), (width, height), (0, 255, 0), 10) # Borda Verde
                cv2.imshow("Portaria", frame)
                cv2.waitKey(2000) # Pausa 2 seg para mostrar o verde
            else:
                print(">>> ACESSO NEGADO!" )
                cv2.rectangle(frame, (0,0), (width, height), (0, 0, 255), 10) # Borda Vermelha
                cv2.imshow("Portaria", frame)
                cv2.waitKey(2000)

        except Exception as e:
            print(f"Erro na leitura: {e}")

    cv2.imshow("Portaria", frame)

    if key & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()