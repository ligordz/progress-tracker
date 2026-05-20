def test_register_success(client):
    """Регистрация нового пользователя"""
    response = client.post("/api/register", json={
        "email": "new@example.com",
        "password": "secure123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@example.com"
    assert data["role"] == "student"
    assert "id" in data

def test_register_duplicate_email(client, test_user):
    """Регистрация с занятым email"""
    response = client.post("/api/register", json={
        "email": "test@example.com",  # уже существует
        "password": "any123"
    })
    assert response.status_code == 400
    assert "уже существует" in response.json()["detail"]

def test_login_success(client, test_user):
    """Успешный вход"""
    response = client.post("/api/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "test@example.com"

def test_login_invalid_credentials(client):
    """Вход с неверным паролем"""
    response = client.post("/api/login", json={
        "email": "test@example.com",
        "password": "wrong_password"
    })
    assert response.status_code == 401
    assert "Неверный" in response.json()["detail"]