import streamlit as st
from PIL import Image
from fpdf import FPDF
import os
import io
from datetime import datetime

# Pasta local para armazenar PDFs
PASTA_SALVA = "documentos_salvos"
os.makedirs(PASTA_SALVA, exist_ok=True)

# Inicializa session_state
if "pdfs" not in st.session_state:
    st.session_state["pdfs"] = []

# Função para criar PDF
def criar_pdf(imagem, nome, cpf, data):
    pdf = FPDF()
    pdf.add_page()

    if imagem.mode != "RGB":
        imagem = imagem.convert("RGB")

    temp_image_path = "temp_image.jpg"
    imagem.save(temp_image_path)

    pdf.image(temp_image_path, x=10, y=10, w=190)
    os.remove(temp_image_path)

    nome_arquivo = f"{nome}_{cpf}_{data}.pdf".replace(" ", "_")
    caminho_completo = os.path.join(PASTA_SALVA, nome_arquivo)

    # Salvar localmente
    pdf.output(caminho_completo)

    # Retorna bytes para download
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    buffer = io.BytesIO(pdf_bytes)
    buffer.seek(0)

    return nome_arquivo, buffer, imagem

# Título
st.title("📄 Scanner para PDF com Renomeação e Gerenciador")

# Upload
arquivo = st.file_uploader("📤 Faça upload do arquivo escaneado (imagem)", type=["jpg", "jpeg", "png"])

# Pré-visualização
if arquivo:
    imagem = Image.open(arquivo)
    st.image(imagem, caption="Pré-visualização", use_column_width=True)

# Formulário
with st.form("formulario_dados"):
    nome = st.text_input("Nome completo")
    cpf = st.text_input("CPF")
    data = st.date_input("Data do documento", value=datetime.today())
    enviar = st.form_submit_button("Gerar PDF")

# Geração do PDF
if enviar:
    if not (arquivo and nome and cpf and data):
        st.warning("⚠️ Todos os campos são obrigatórios.")
    else:
        imagem = Image.open(arquivo)
        data_formatada = data.strftime("%Y-%m-%d")
        nome_arquivo, buffer_pdf, imagem = criar_pdf(imagem, nome, cpf, data_formatada)

        st.session_state["pdfs"].append({
            "nome_arquivo": nome_arquivo,
            "buffer": buffer_pdf,
            "data": data_formatada,
            "nome": nome,
            "imagem_preview": imagem
        })

        st.success("✅ PDF gerado e salvo com sucesso!")

# Grid dos PDFs gerados
if st.session_state["pdfs"]:
    st.subheader("📁 Documentos Escaneados")
    cols = st.columns(3)

    for i, doc in enumerate(st.session_state["pdfs"]):
        col = cols[i % 3]
        with col:
            st.image(doc["imagem_preview"], caption="Prévia", use_column_width=True)
            st.markdown(f"**{doc['nome']}**")
            st.markdown(f"📅 {doc['data']}")
            st.download_button(
                label="📥 Baixar PDF",
                data=doc["buffer"],
                file_name=doc["nome_arquivo"],
                mime="application/pdf",
                key=f"download_{i}"
            )
            if st.button(f"🗑️ Excluir", key=f"delete_{i}"):
                del st.session_state["pdfs"][i]
                st.experimental_rerun()
