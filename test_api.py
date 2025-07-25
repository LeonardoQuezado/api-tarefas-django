import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api"

def test_email_only():
    print("📧 TESTE ESPECÍFICO DO EMAIL")
    print("="*50)
    
    # Registrar usuário para testar email
    username = f"emailtest_{int(time.time())}"
    data = {
        "username": username,
        "email": "teste.email@exemplo.com",
        "password": "testpass123", 
        "password_confirm": "testpass123",
        "first_name": "Teste",
        "last_name": "Email"
    }
    
    print(f"📝 Registrando usuário: {username}")
    print(f"📧 Email: {data['email']}")
    print("\n🔍 VERIFIQUE OS LOGS NO TERMINAL DO SERVIDOR DJANGO!")
    print("Deve aparecer mensagens sobre o envio do email...")
    
    response = requests.post(f"{BASE_URL}/auth/register/", json=data)
    
    if response.status_code == 201:
        print(f"✅ Usuário criado com sucesso!")
        print(f"📧 Email deve ter sido enviado para: {data['email']}")
    else:
        print(f"❌ Erro: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_email_only()