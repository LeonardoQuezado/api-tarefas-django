import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_user_registration():
    """Testa o registro de usuário"""
    url = f"{BASE_URL}/auth/register/"
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "password_confirm": "testpass123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        response = requests.post(url, json=data)
        print("=== TESTE DE REGISTRO ===")
        print(f"Status: {response.status_code}")
        print(f"URL: {url}")
        
        if response.status_code == 404:
            print("❌ URL não encontrada - verificar configuração de URLs")
            return None
            
        if response.text:
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        else:
            print("Response vazia")
            
        if response.status_code == 201:
            return response.json()['tokens']['access']
        return None
    except requests.exceptions.JSONDecodeError as e:
        print(f"❌ Erro JSON: {e}")
        print(f"Response text: {response.text}")
        return None

def test_user_login():
    """Testa o login de usuário"""
    url = f"{BASE_URL}/auth/login/"
    data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    response = requests.post(url, json=data)
    print("\n=== TESTE DE LOGIN ===")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        return response.json()['tokens']['access']
    return None

def test_create_task(token):
    """Testa criação de tarefa"""
    url = f"{BASE_URL}/tasks/"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "title": "Minha primeira tarefa",
        "description": "Descrição da tarefa teste",
        "execution_date": "2025-07-25T10:00:00-03:00",  # Timezone do Brasil
        "status": "pendente",
        "category_ids": [1]  # ID da primeira categoria
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print("\n=== TESTE DE CRIAÇÃO DE TAREFA ===")
        print(f"Status: {response.status_code}")
        
        if response.text:
            if response.status_code == 500:
                print("❌ Erro 500 - verifique o terminal do servidor para detalhes")
                print(f"Response text: {response.text[:500]}")
            else:
                print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        else:
            print("Response vazia")
    except requests.exceptions.JSONDecodeError as e:
        print(f"❌ Erro JSON: {e}")
        print(f"Response text: {response.text}")

def test_get_agenda(token):
    """Testa endpoint de agenda"""
    url = f"{BASE_URL}/tasks/agenda/"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print("\n=== TESTE DE AGENDA ===")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    print("🚀 Testando API de Tarefas\n")
    
    # Teste de registro
    token = test_user_registration()
    
    if not token:
        # Se registro falhar, tenta login
        token = test_user_login()
    
    if token:
        # Testa criação de tarefa
        test_create_task(token)
        
        # Testa agenda
        test_get_agenda(token)
    else:
        print("❌ Não foi possível obter token de acesso")