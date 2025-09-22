# teste_secrets.py
import streamlit as st

st.set_page_config(page_title="Teste de Secrets")
st.title("🕵️ Verificador de Secrets do Streamlit")

st.header("Verificando 'gcp_service_account'")

# Verifica se a seção principal do secret existe
if "gcp_service_account" in st.secrets:
    st.success("✅ Secret 'gcp_service_account' encontrado!")
    
    # Pega o dicionário do secret
    creds = st.secrets["gcp_service_account"]
    
    # Verifica a presença e os valores de campos não-sensíveis
    st.write("--- Verificando campos individuais ---")
    
    if "project_id" in creds:
        st.info(f"Project ID: {creds['project_id']}")
    else:
        st.error("❌ Campo 'project_id' NÃO encontrado no secret.")

    if "client_email" in creds:
        st.info(f"Client Email: {creds['client_email']}")
    else:
        st.error("❌ Campo 'client_email' NÃO encontrado no secret.")
        
    # A verificação mais importante: a chave privada existe?
    if "private_key" in creds and creds["private_key"]:
        st.success("✅ Campo 'private_key' encontrado e não está vazio.")
    else:
        st.error("❌ ERRO CRÍTICO: Campo 'private_key' NÃO encontrado ou está VAZIO.")

else:
    st.error("❌ ERRO CRÍTICO: O secret 'gcp_service_account' não foi encontrado! Verifique o nome do secret.")