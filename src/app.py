#*importar bibliotecas*
import os
import json
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from deepface import DeepFace

#*inicializar aplicacao Flask*
app = Flask(__name__)

#*configurar pasta onde as imagens dos rostos serao armazenadas*
PASTA_ROSTOS = "rostos"

#*arquivo utilizado para armazenar os dados cadastrados*
ARQUIVO_CADASTROS = "cadastros.json"

#*criar pasta de rostos caso ela nao exista*
os.makedirs(PASTA_ROSTOS, exist_ok=True)

#*rota da tela de cadastro*
@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")

#*rota responsavel por receber o cadastro*
@app.route("/cadastrar", methods=["POST"])
def cadastrar():
    #*receber dados enviados pelo formulario*
    nome = request.form.get("nome")
    email = request.form.get("email")
    matricula = request.form.get("matricula")
    foto = request.files.get("foto")

    #*verificar se todos os campos foram preenchidos*
    if not nome or not email or not matricula or not foto:
        return "Erro: Preencha todos os campos."

    #*obter extensao original da imagem*
    nome_arquivo = secure_filename(foto.filename)
    extensao = os.path.splitext(nome_arquivo)[1].lower()

    #*verificar formato permitido*
    if extensao not in [".jpg", ".jpeg", ".png"]:
        return "Erro: Utilize uma imagem JPG, JPEG ou PNG."

    #*criar nome da imagem utilizando a matricula*
    nome_foto = secure_filename(matricula) + extensao
    caminho_foto = os.path.join(PASTA_ROSTOS, nome_foto)

    #*salvar temporariamente a imagem*
    foto.save(caminho_foto)

    #*verificar se existe um rosto valido na imagem*
    try:
        DeepFace.extract_faces(
            img_path=caminho_foto,
            enforce_detection=True
        )
    except Exception:
        #*remover imagem caso nenhum rosto seja encontrado*
        if os.path.exists(caminho_foto):
            os.remove(caminho_foto)
        return "Erro: Nenhum rosto valido foi encontrado na imagem."

    #*carregar cadastros existentes*
    if os.path.exists(ARQUIVO_CADASTROS):
        try:
            with open(ARQUIVO_CADASTROS, "r", encoding="utf-8") as arquivo:
                cadastros = json.load(arquivo)
        except (json.JSONDecodeError, FileNotFoundError):
            cadastros = []
    else:
        cadastros = []

    #*verificar se a matricula ja esta cadastrada*
    for pessoa in cadastros:
        if pessoa["matricula"] == matricula:
            #*remover imagem salva para evitar sobrescrever cadastro existente*
            if os.path.exists(caminho_foto):
                os.remove(caminho_foto)
            return "Erro: Esta matricula ja esta cadastrada."

    #*criar dados da pessoa cadastrada*
    pessoa = {
        "nome": nome,
        "email": email,
        "matricula": matricula,
        "foto": nome_foto
    }

    #*adicionar pessoa na lista de cadastros*
    cadastros.append(pessoa)

    #*salvar dados no arquivo JSON*
    with open(ARQUIVO_CADASTROS, "w", encoding="utf-8") as arquivo:
        json.dump(cadastros, arquivo, ensure_ascii=False, indent=4)

    #*retornar para tela de cadastro informando sucesso*
    return redirect(url_for("cadastro", sucesso="1"))

#*iniciar servidor Flask*
if __name__ == "__main__":
    app.run(debug=True)