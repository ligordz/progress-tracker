def test_heatmap_endpoint(client, auth_token):
    """Эндпоинт heatmap возвращает данные"""
    response = client.get("/api/analytics/heatmap", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


def test_weekly_stats_endpoint(client, auth_token):
    """Эндпоинт weekly возвращает список недель"""
    response = client.get("/api/analytics/weekly?weeks=4", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_streaks_endpoint(client, auth_token):
    """Эндпоинт streaks возвращает текущую и лучшую серию"""
    response = client.get("/api/analytics/streaks", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 200
    data = response.json()
    assert "current" in data
    assert "best" in data
    assert isinstance(data["current"], int)
    assert isinstance(data["best"], int)


def test_achievements_endpoint(client, auth_token):
    """Эндпоинт achievements возвращает список достижений"""
    response = client.get("/api/analytics/achievements", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # После создания сессии должно появиться достижение "Первая сессия"
    client.post("/api/sessions/", json={
        "start_time": "2026-05-20T10:00:00",
        "end_time": "2026-05-20T10:25:00",
        "focus_score": 7,
        "tag_ids": []
    }, headers={"Authorization": f"Bearer {auth_token}"})

    response = client.get("/api/analytics/achievements", headers={"Authorization": f"Bearer {auth_token}"})
    achievements = response.json()
    assert any(a["id"] == "first_session" for a in achievements)