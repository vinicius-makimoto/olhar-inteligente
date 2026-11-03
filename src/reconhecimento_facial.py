#*importar bibliotecas*
import cv2
import json
import os
import threading
from deepface import DeepFace
from playsound import playsound

#*definir arquivos e pastas utilizados pelo sistema*
PASTA_ROSTOS = "rostos"
ARQUIVO_CADASTROS = "cadastros.json"
AUDIO_LIBERADO = "acesso_liberado.mp3"
AUDIO_NEGADO = "acesso_negado.mp3"

#*funcao responsavel por reproduzir os audios*
def reproduzir_audio(arquivo):
    try:
        #*executa o audio em outra thread para nao travar a camera*
        threading.Thread(
            target=playsound,
            args=(arquivo,),
            daemon=True
        ).start()
    except Exception as e:
        print("Erro ao reproduzir audio:", e)

#*verificar se a pasta de rostos existe*
if not os.path.exists(PASTA_ROSTOS):
    print("Erro: A pasta de rostos cadastrados nao foi encontrada.")
    exit()

#*verificar se o arquivo de cadastros existe*
if not os.path.exists(ARQUIVO_CADASTROS):
    print("Erro: Nenhum cadastro foi encontrado.")
    exit()

#*verificar se os arquivos de audio existem*
if not os.path.exists(AUDIO_LIBERADO):
    print("Aviso: O arquivo acesso_liberado.mp3 nao foi encontrado.")

if not os.path.exists(AUDIO_NEGADO):
    print("Aviso: O arquivo acesso_negado.mp3 nao foi encontrado.")

#*carregar dados das pessoas cadastradas*
try:
    with open(ARQUIVO_CADASTROS, "r", encoding="utf-8") as arquivo:
        cadastros = json.load(arquivo)
    print("Cadastros carregados com sucesso.")
except Exception as e:
    print("Erro ao carregar os cadastros.")
    print("Erro real:", e)
    exit()

#*verificar se existem pessoas cadastradas*
if len(cadastros) == 0:
    print("Erro: Nenhuma pessoa esta cadastrada.")
    exit()

#*validar imagens cadastradas*
print("Carregando rostos cadastrados...")

rostos_validos = []

for pessoa in cadastros:
    nome_foto = pessoa.get("foto")

    #*verificar se existe nome de foto no cadastro*
    if not nome_foto:
        print("Cadastro sem imagem:", pessoa.get("nome"))
        continue

    caminho_foto = os.path.join(PASTA_ROSTOS, nome_foto)

    #*verificar se a imagem cadastrada existe*
    if not os.path.exists(caminho_foto):
        print("Imagem nao encontrada:", caminho_foto)
        continue

    try:
        #*verificar se a imagem cadastrada possui um rosto valido*
        DeepFace.extract_faces(
            img_path=caminho_foto,
            enforce_detection=True
        )

        #*adicionar pessoa na lista de rostos validos*
        rostos_validos.append({
            "nome": pessoa.get("nome"),
            "email": pessoa.get("email"),
            "matricula": pessoa.get("matricula"),
            "foto": caminho_foto
        })

        print("Rosto carregado:", pessoa.get("nome"))

    except Exception as e:
        print("Erro ao validar rosto de:", pessoa.get("nome"))
        print("Erro real:", e)

#*verificar se pelo menos um rosto valido foi carregado*
if len(rostos_validos) == 0:
    print("Erro: Nenhum rosto valido foi encontrado.")
    exit()

print("Total de rostos carregados:", len(rostos_validos))

#*inicialiazacao de camera*
cap = cv2.VideoCapture(0) #*abre a cam principal*

#*verificar se a camera foi aberta corretamente*
if not cap.isOpened():
    print("Erro: Nao foi possivel abrir a camera.")
    exit()

#*variaveis de controle de estado*
status_acesso = "Aguardando..."
cor_status = (255,255,255) #*cor branca do sistema BGR*
contador_quadros = 0
pessoa_identificada = None
ultimo_status = None

while True: #*inicia loop para processar o video (seq. de fotos)*
    ret, frame = cap.read() #*extrai a imagem fornecida pela webcam*

    if not ret: #*camera falhou ou foi desconectada: sistema para*
        break

    contador_quadros += 1

    #*reconhecimento facial*
    if contador_quadros % 30 == 0: #*executa a comparacao a cada 30 quadros*
        pessoa_identificada = None

        #*percorrer todos os rostos cadastrados*
        for pessoa in rostos_validos:
            try:
                resultado = DeepFace.verify(
                    img1_path=frame, #*imagem sendo exibida na camera*
                    img2_path=pessoa["foto"], #*imagem de referencia cadastrada*
                    enforce_detection=False #*impede que o programa quebre se o rosto sumir*
                )

                #*analisar o retorno do algoritmo de IA*
                if resultado["verified"]:
                    pessoa_identificada = pessoa
                    break

            except Exception as e:
                print("Erro durante comparacao:", e)

        #*verificar se alguma pessoa foi reconhecida*
        if pessoa_identificada:
            status_acesso = "Acesso Liberado - " + pessoa_identificada["nome"]
            cor_status = (0,255,0) #*verde*

            #*reproduzir audio apenas quando o estado mudar para acesso liberado*
            if ultimo_status != "liberado":
                if os.path.exists(AUDIO_LIBERADO):
                    reproduzir_audio(AUDIO_LIBERADO)
                ultimo_status = "liberado"

            print(
                "Pessoa reconhecida:",
                pessoa_identificada["nome"],
                "- Matricula:",
                pessoa_identificada["matricula"]
            )

        else:
            status_acesso = "Acesso Negado"
            cor_status = (0,0,255) #*vermelho*

            #*reproduzir audio apenas quando o estado mudar para acesso negado*
            if ultimo_status != "negado":
                if os.path.exists(AUDIO_NEGADO):
                    reproduzir_audio(AUDIO_NEGADO)
                ultimo_status = "negado"

    #*interface que sera exibida no video*
    cv2.putText(
        frame,
        status_acesso,
        (30,50), #*coordenadas no texto (onde vai ficar localizado)*
        cv2.FONT_HERSHEY_COMPLEX, #*fonte da biblioteca da opencv*
        1.0, #*tamanho da fonte*
        cor_status, #*cor da mensagem*
        2 #*espessura da linha*
    )

    #*exibe a imagem com a marcacao em uma janela*
    cv2.imshow("Reconhecimento facial", frame)

    #*verificar se a tecla q foi pressionada*
    if cv2.waitKey(1) & 0xFF == ord("q"): #*pressiona a tecla q e o sistema e fechado*
        break

#*finalizar recursos utilizados pelo sistema*
cap.release() #*libera a webcam*
cv2.destroyAllWindows() #*fecha as janelas*