from datetime import datetime, timedelta


def test_create_goal_success(client, auth_token):
    """Создание учебной цели"""
    response = client.post("/api/goals/", json={
        "title": "Подготовка к экзамену",
        "target_minutes": 300,
        "deadline": "2026-06-01T23:59:59"
    }, headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Подготовка к экзамену"
    assert data["target_minutes"] == 300
    assert data["progress_percent"] == 0.0


def test_get_goals_list(client, auth_token):
    """Получение списка активных целей"""
    client.post("/api/goals/", json={
        "title": "Тестовая цель",
        "target_minutes": 100,
        "deadline": None
    }, headers={"Authorization": f"Bearer {auth_token}"})

    response = client.get("/api/goals/", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(g["title"] == "Тестовая цель" for g in data)


def test_toggle_goal_success(client, auth_token):
    """Переключение статуса цели"""
    create = client.post("/api/goals/", json={
        "title": "Цель для переключения",
        "target_minutes": 50,
        "deadline": None
    }, headers={"Authorization": f"Bearer {auth_token}"})
    goal_id = create.json()["id"]

    response = client.post(f"/api/goals/{goal_id}/toggle", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 200
    assert response.json()["is_active"] == False

    response = client.post(f"/api/goals/{goal_id}/toggle", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.json()["is_active"] == True


def test_goal_progress_calculation(client, auth_token, db_session):
    """
    Вариант B: Расчёт прогресса цели — считаем ВСЕ сессии пользователя.
    Тест создаёт сессию с временем, которое гарантированно попадает в диапазон.
    """
    # Создаём цель
    goal_resp = client.post("/api/goals/", json={
        "title": "Цель с прогрессом",
        "target_minutes": 100,
        "deadline": None
    }, headers={"Authorization": f"Bearer {auth_token}"})
    assert goal_resp.status_code == 201
    goal_id = goal_resp.json()["id"]

    # Создаём сессию на 30 минут (время берём "сейчас", чтобы гарантированно попасть в фильтр)
    now = datetime.utcnow()
    client.post("/api/sessions/", json={
        "start_time": now.isoformat(),
        "end_time": (now + timedelta(minutes=30)).isoformat(),
        "focus_score": 8,
        "note": "Тестовая сессия",
        "tag_ids": []
    }, headers={"Authorization": f"Bearer {auth_token}"})

    # Проверяем прогресс: 30 минут из 100 = 30%
    goals = client.get("/api/goals/", headers={"Authorization": f"Bearer {auth_token}"})
    assert goals.status_code == 200
    target_goal = next((g for g in goals.json() if g["id"] == goal_id), None)
    assert target_goal is not None, "Цель не найдена в списке"
    assert target_goal["achieved_minutes"] == 30.0, f"Ожидалось 30.0, получено {target_goal['achieved_minutes']}"
    assert target_goal["progress_percent"] == 30.0, f"Ожидалось 30.0%, получено {target_goal['progress_percent']}%"