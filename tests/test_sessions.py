def test_create_session_success(client, auth_token):
    """Создание учебной сессии"""
    response = client.post("/api/sessions/", json={
        "start_time": "2026-05-20T10:00:00",
        "end_time": "2026-05-20T10:25:00",
        "focus_score": 8,
        "note": "Изучал тестирование",
        "goal": "Написать тесты",
        "tag_ids": []
    }, headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 201
    data = response.json()
    assert data["duration_minutes"] == 25.0
    assert data["focus_score"] == 8
    assert data["goal"] == "Написать тесты"


def test_get_sessions_list(client, auth_token):
    """Получение списка сессий пользователя"""
    # Сначала создаём сессию
    client.post("/api/sessions/", json={
        "start_time": "2026-05-20T10:00:00",
        "end_time": "2026-05-20T10:30:00",
        "focus_score": 7,
        "tag_ids": []
    }, headers={"Authorization": f"Bearer {auth_token}"})

    response = client.get("/api/sessions/", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["duration_minutes"] == 30.0


def test_update_session_success(client, auth_token):
    """Обновление сессии"""
    # Создаём
    create = client.post("/api/sessions/", json={
        "start_time": "2026-05-20T10:00:00",
        "end_time": "2026-05-20T10:20:00",
        "focus_score": 5,
        "note": "старая заметка",
        "tag_ids": []
    }, headers={"Authorization": f"Bearer {auth_token}"})
    session_id = create.json()["id"]

    # Обновляем
    response = client.put(f"/api/sessions/{session_id}", json={
        "focus_score": 9,
        "note": "новая заметка"
    }, headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["focus_score"] == 9
    assert data["note"] == "новая заметка"


def test_delete_session_success(client, auth_token):
    """Удаление сессии"""
    # Создаём
    create = client.post("/api/sessions/", json={
        "start_time": "2026-05-20T10:00:00",
        "end_time": "2026-05-20T10:15:00",
        "focus_score": 6,
        "tag_ids": []
    }, headers={"Authorization": f"Bearer {auth_token}"})
    session_id = create.json()["id"]

    # Удаляем
    response = client.delete(f"/api/sessions/{session_id}", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 204

    # Проверяем, что сессии нет
    get = client.get("/api/sessions/", headers={"Authorization": f"Bearer {auth_token}"})
    assert len(get.json()) == 0


def test_clear_sessions_success(client, auth_token):
    """Очистка всех сессий пользователя"""
    # Создаём 2 сессии
    for i in range(2):
        client.post("/api/sessions/", json={
            "start_time": f"2026-05-20T1{i}:00:00",
            "end_time": f"2026-05-20T1{i}:30:00",
            "focus_score": 7,
            "tag_ids": []
        }, headers={"Authorization": f"Bearer {auth_token}"})

    # Очищаем
    response = client.post("/api/sessions/clear", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 200
    assert response.json()["count"] == 2

    # Проверяем пустоту
    get = client.get("/api/sessions/", headers={"Authorization": f"Bearer {auth_token}"})
    assert len(get.json()) == 0


def test_unauthorized_access(client):
    """Доступ к защищённым эндпоинтам без токена"""
    response = client.get("/api/sessions/")
    assert response.status_code == 403