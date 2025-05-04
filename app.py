# app.py
import streamlit as st
import sqlite3
from datetime import datetime
import json
import os
from pathlib import Path

# Configuração da página
st.set_page_config(
    page_title="Sistema Jurídico - Oliveira's",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
def load_css():
    st.markdown("""
    <style>
    :root {
        --primary-color: #00897b;
        --secondary-color: #26a69a;
        --dark-color: #1a2b3d;
        --light-color: #e8f5f3;
        --text-primary: #ffffff;
        --text-dark: #212121;
        --accent-color: #ff5252;
        --gold-color: #c9a961;
        --bg-gradient: linear-gradient(135deg, #1a2b3d 0%, #2c3e50 100%);
    }
    
    .main-header {
        background: rgba(0, 137, 123, 0.9);
        color: white;
        padding: 40px;
        border-radius: 20px;
        margin-bottom: 30px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .logo-container {
        text-align: center;
        margin-bottom: 30px;
    }
    
    .logo-text {
        font-size: 36px;
        font-weight: 700;
        color: var(--text-primary);
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        margin-top: 10px;
    }
    
    .document-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .document-preview {
        background: white;
        color: var(--text-dark);
        padding: 60px;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        margin: 20px 0;
        min-height: 800px;
        font-family: 'Times New Roman', serif;
        position: relative;
        border: 2px solid var(--gold-color);
    }
    
    .watermark {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%) rotate(-45deg);
        font-size: 100px;
        color: rgba(0, 137, 123, 0.05);
        pointer-events: none;
        z-index: 0;
    }
    
    .signature-line {
        border-bottom: 2px solid var(--text-dark);
        width: 300px;
        margin: 40px 0 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Garantir que o banco de dados existe
def init_db():
    # Criar diretório se não existir
    db_dir = Path("data")
    db_dir.mkdir(exist_ok=True)
    
    # Caminho do banco de dados
    db_path = db_dir / "juridico.db"
    
    # Conectar ou criar banco de dados
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    
    # Criar tabela se não existir
    c.execute('''
        CREATE TABLE IF NOT EXISTS documentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            titulo TEXT NOT NULL,
            conteudo TEXT NOT NULL,
            cliente TEXT,
            data_criacao TIMESTAMP,
            data_modificacao TIMESTAMP,
            status TEXT DEFAULT 'rascunho',
            metadata TEXT,
            background_image TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    return str(db_path)

# Obter caminho do banco de dados
def get_db_path():
    return str(Path("data") / "juridico.db")

# Templates de documentos jurídicos
TEMPLATES = {
    "peticao_inicial": {
        "nome": "Petição Inicial",
        "campos": ["numero_processo", "vara", "autor", "reu", "fatos", "direito", "pedidos", "valor_causa"],
        "formato": """
        <div class="document-preview">
            <div class="watermark">OLIVEIRA'S</div>
            <div style="text-align: center; margin-bottom: 40px;">
                <h3>EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DE DIREITO DA {vara}</h3>
            </div>
            
            <div style="text-align: right; margin-bottom: 40px;">
                <strong>Processo nº:</strong> {numero_processo}
            </div>
            
            <div style="margin-bottom: 40px;">
                <p style="text-align: justify; line-height: 2;">
                    <strong>{autor}</strong>, já qualificado nos autos, por seu advogado que esta subscreve,
                    vem, respeitosamente, à presença de Vossa Excelência, com fundamento nos artigos
                    pertinentes do Código de Processo Civil, propor a presente
                </p>
                
                <h2 style="text-align: center; margin: 30px 0;">AÇÃO ANULATÓRIA DE ATO ADMINISTRATIVO</h2>
                
                <p style="text-align: justify;">
                    em face de <strong>{reu}</strong>, pelos fatos e fundamentos jurídicos que passa a expor:
                </p>
            </div>
            
            <div>
                <h3>I - DOS FATOS</h3>
                <p style="text-align: justify; line-height: 1.8;">{fatos}</p>
            </div>
            
            <div>
                <h3>II - DO DIREITO</h3>
                <p style="text-align: justify; line-height: 1.8;">{direito}</p>
            </div>
            
            <div>
                <h3>III - DOS PEDIDOS</h3>
                <p style="text-align: justify; line-height: 1.8;">{pedidos}</p>
            </div>
            
            <div style="margin-top: 60px;">
                <p>Dá-se à causa o valor de R$ {valor_causa}.</p>
                <p>Nestes termos,<br>Pede deferimento.</p>
                
                <p style="text-align: right; margin-top: 40px;">São Luís/MA, {data}</p>
                
                <div style="text-align: center; margin-top: 60px;">
                    <div class="signature-line"></div>
                    <p><strong>JESUS MARTINS OLIVEIRA</strong><br>OAB/MA 25.019</p>
                </div>
            </div>
        </div>
        """
    },
    "contrato_honorarios": {
        "nome": "Contrato de Honorários Advocatícios",
        "campos": ["contratante", "cpf_contratante", "objeto", "valor", "forma_pagamento", "prazo"],
        "formato": """
        <div class="document-preview">
            <div class="watermark">OLIVEIRA'S</div>
            <div style="text-align: center; margin-bottom: 40px;">
                <h2>CONTRATO DE PRESTAÇÃO DE SERVIÇOS ADVOCATÍCIOS</h2>
            </div>
            
            <p style="text-align: justify; line-height: 1.8;">
                Pelo presente instrumento particular de Contrato de Prestação de Serviços Advocatícios,
                de um lado <strong>{contratante}</strong>, inscrito(a) no CPF sob nº {cpf_contratante},
                doravante denominado(a) CONTRATANTE, e de outro lado, <strong>OLIVEIRA'S ADVOCACIA</strong>,
                com sede na Rua dos Guarás, Casa 01, Q 17, Ponta do Farol, São Luís/MA, CEP 65077-460,
                neste ato representada por seu sócio administrador Dr. JESUS MARTINS OLIVEIRA,
                OAB/MA 25.019, doravante denominada CONTRATADA, têm entre si justo e contratado o seguinte:
            </p>
            
            <div>
                <h3>CLÁUSULA PRIMEIRA - DO OBJETO</h3>
                <p style="text-align: justify;">{objeto}</p>
            </div>
            
            <div>
                <h3>CLÁUSULA SEGUNDA - DOS HONORÁRIOS</h3>
                <p style="text-align: justify;">
                    Pelos serviços prestados, o CONTRATANTE pagará à CONTRATADA o valor de
                    <strong>R$ {valor}</strong>, da seguinte forma: {forma_pagamento}
                </p>
            </div>
            
            <div>
                <h3>CLÁUSULA TERCEIRA - DO PRAZO</h3>
                <p style="text-align: justify;">{prazo}</p>
            </div>
            
            <p style="text-align: center; margin-top: 40px;">São Luís/MA, {data}</p>
            
            <div style="display: flex; justify-content: space-around; margin-top: 80px;">
                <div style="text-align: center;">
                    <div class="signature-line"></div>
                    <p>CONTRATANTE</p>
                </div>
                <div style="text-align: center;">
                    <div class="signature-line"></div>
                    <p>OLIVEIRA'S ADVOCACIA<br>CONTRATADA</p>
                </div>
            </div>
        </div>
        """
    }
}

# Funções do banco de dados
def salvar_documento(tipo, titulo, conteudo, cliente=None, metadata=None, background_image=None):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    metadata_json = json.dumps(metadata) if metadata else "{}"
    
    c.execute("""
        INSERT INTO documentos (tipo, titulo, conteudo, cliente, data_criacao, data_modificacao, metadata, background_image)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (tipo, titulo, conteudo, cliente, now, now, metadata_json, background_image))
    
    conn.commit()
    doc_id = c.lastrowid
    conn.close()
    
    return doc_id

def listar_documentos(tipo=None, cliente=None):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    if tipo and cliente:
        cursor.execute("SELECT * FROM documentos WHERE tipo = ? AND cliente LIKE ? ORDER BY data_modificacao DESC", 
                      (tipo, f"%{cliente}%"))
    elif tipo:
        cursor.execute("SELECT * FROM documentos WHERE tipo = ? ORDER BY data_modificacao DESC", (tipo,))
    elif cliente:
        cursor.execute("SELECT * FROM documentos WHERE cliente LIKE ? ORDER BY data_modificacao DESC", (f"%{cliente}%",))
    else:
        cursor.execute("SELECT * FROM documentos ORDER BY data_modificacao DESC")
    
    documentos = cursor.fetchall()
    conn.close()
    
    # Converter para lista de dicionários
    docs_list = []
    for doc in documentos:
        docs_list.append({
            'id': doc[0],
            'tipo': doc[1],
            'titulo': doc[2],
            'conteudo': doc[3],
            'cliente': doc[4],
            'data_criacao': doc[5],
            'data_modificacao': doc[6],
            'status': doc[7] if len(doc) > 7 else None,
            'metadata': doc[8] if len(doc) > 8 else None,
            'background_image': doc[9] if len(doc) > 9 else None
        })
    
    return docs_list

# Interface principal
def main():
    load_css()
    
    # Inicializar banco de dados
    db_path = init_db()
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div class="logo-container">
            <div class="logo-text">⚖️ OLIVEIRA'S</div>
            <p style="color: white;">Sistema Jurídico</p>
        </div>
        """, unsafe_allow_html=True)
        
        pagina = st.selectbox(
            "Navegação",
            ["Novo Documento", "Documentos Salvos", "Templates", "Configurações"]
        )
        
        st.markdown("---")
        
        # Seletor de tema de fundo
        st.markdown("### Tema Visual")
        background_letter = st.selectbox(
            "Selecione o Tema",
            list("abcdefghijklmnopqrstuvwxyz"),
            format_func=lambda x: f"Tema {x.upper()}"
        )
    
    # Conteúdo principal
    if pagina == "Novo Documento":
        st.markdown("""
        <div class="main-header">
            <h1>Novo Documento Jurídico</h1>
            <p>Crie documentos jurídicos profissionais com os templates Oliveira's</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Seleção de template
        col1, col2 = st.columns([2, 1])
        
        with col1:
            template_tipo = st.selectbox(
                "Selecione o tipo de documento",
                options=list(TEMPLATES.keys()),
                format_func=lambda x: f"📜 {TEMPLATES[x]['nome']}"
            )
        
        with col2:
            st.info("💡 Preencha os campos para gerar o documento")
        
        # Campos do formulário
        template = TEMPLATES[template_tipo]
        campos_valores = {}
        
        st.markdown("### 📝 Informações do Documento")
        
        # Criar formulário dinâmico
        for campo in template["campos"]:
            if campo in ["fatos", "direito", "pedidos", "objeto"]:
                campos_valores[campo] = st.text_area(
                    campo.replace("_", " ").title(),
                    height=150
                )
            elif campo == "valor_causa" or campo == "valor":
                valor = st.number_input(
                    f"{campo.replace('_', ' ').title()} (R$)", 
                    min_value=0.0, 
                    step=100.0
                )
                campos_valores[campo] = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            else:
                campos_valores[campo] = st.text_input(campo.replace("_", " ").title())
        
        # Botões de ação
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Gerar Documento"):
                campos_valores["data"] = datetime.now().strftime("%d/%m/%Y")
                documento_html = template["formato"].format(**campos_valores)
                st.session_state.documento_atual = documento_html
                st.session_state.campos_atuais = campos_valores
        
        with col2:
            if st.button("💾 Salvar Documento"):
                if 'documento_atual' in st.session_state:
                    titulo = f"{TEMPLATES[template_tipo]['nome']} - {campos_valores.get('cliente', campos_valores.get('contratante', campos_valores.get('autor', 'Sem título')))}"
                    doc_id = salvar_documento(
                        tipo=template_tipo,
                        titulo=titulo,
                        conteudo=st.session_state.documento_atual,
                        cliente=campos_valores.get('cliente', campos_valores.get('contratante', campos_valores.get('autor', ''))),
                        metadata=campos_valores,
                        background_image=background_letter
                    )
                    st.success(f"✅ Documento salvo com sucesso! ID: {doc_id}")
        
        # Preview do documento
        if 'documento_atual' in st.session_state:
            st.markdown("### 👁️ Visualização do Documento")
            st.markdown(st.session_state.documento_atual, unsafe_allow_html=True)
            
            # Download
            st.download_button(
                label="📥 Download HTML",
                data=st.session_state.documento_atual.encode(),
                file_name=f"documento_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html"
            )
    
    elif pagina == "Documentos Salvos":
        st.markdown("""
        <div class="main-header">
            <h1>Documentos Salvos</h1>
            <p>Gerencie seus documentos jurídicos</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            tipo_filtro = st.selectbox(
                "Filtrar por tipo",
                ["Todos"] + list(TEMPLATES.keys()),
                format_func=lambda x: TEMPLATES[x]["nome"] if x in TEMPLATES else x
            )
        with col2:
            cliente_filtro = st.text_input("Filtrar por cliente")
        
        # Listar documentos
        tipo = None if tipo_filtro == "Todos" else tipo_filtro
        documentos = listar_documentos(tipo=tipo, cliente=cliente_filtro)
        
        if documentos:
            for doc in documentos:
                with st.expander(f"📄 {doc['titulo']} - {doc['data_criacao'][:10] if doc['data_criacao'] else 'Sem data'}"):
                    st.markdown(doc['conteudo'], unsafe_allow_html=True)
                    
                    st.download_button(
                        "📥 Download",
                        data=doc['conteudo'].encode(),
                        file_name=f"{doc['titulo']}.html",
                        mime="text/html",
                        key=f"download_{doc['id']}"
                    )
        else:
            st.info("📭 Nenhum documento encontrado")
    
    elif pagina == "Templates":
        st.markdown("""
        <div class="main-header">
            <h1>Templates Disponíveis</h1>
            <p>Biblioteca de modelos jurídicos profissionais</p>
        </div>
        """, unsafe_allow_html=True)
        
        for template_id, template in TEMPLATES.items():
            st.markdown(f"""
            <div class="document-card">
                <h3>📜 {template['nome']}</h3>
                <p><strong>Campos necessários:</strong> {', '.join(template['campos'])}</p>
                <p>Template profissional com formatação jurídica padrão</p>
            </div>
            """, unsafe_allow_html=True)
    
    elif pagina == "Configurações":
        st.markdown("""
        <div class="main-header">
            <h1>Configurações do Sistema</h1>
            <p>Personalize seu ambiente jurídico</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### Informações do Escritório")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nome_escritorio = st.text_input("Nome do Escritório", value="Oliveira's Advocacia")
            telefone = st.text_input("Telefone", value="(98) 3000-0000")
            email = st.text_input("Email", value="contato@oliveiras.adv.br")
        
        with col2:
            endereco = st.text_area("Endereço", value="Rua dos Guarás, Casa 01, Q 17\nPonta do Farol\nSão Luís/MA\nCEP: 65077-460")
            oab = st.text_input("Registro OAB", value="OAB/MA 25.019")
        
        if st.button("💾 Salvar Configurações"):
            st.success("✅ Configurações salvas com sucesso!")

if __name__ == "__main__":
    main()
