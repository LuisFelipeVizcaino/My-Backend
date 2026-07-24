def esquema_usuario(user) -> dict:
    return {"id":str (user["_id"]),
            "name": user["name"],
            "age": user["age"],
            "password": user["password"]}

def esquema_usuarios(users) -> list:
    return [esquema_usuario(user) for user in users]
