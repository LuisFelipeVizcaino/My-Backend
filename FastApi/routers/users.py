from fastapi import APIRouter, HTTPException, status, Depends
from db.modelo.modelo_usuario import User, Userdb
from db.cliente import db_client
from db.esquemas.user import esquema_usuario, esquema_usuarios
from bson import ObjectId
from jose import jwt, JWTError
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta,datetime, timezone
router = APIRouter(prefix="/usersdb",
                   tags=["usersdb"],
                   responses={status.HTTP_200_OK: {"message": "not found"}})

load_dotenv()
SECRET = os.getenv("SECRET")
algoritmo = "HS256"
duracion_token_acceso = 1
oauth2 = OAuth2PasswordBearer(tokenUrl="login")
encriptacion = CryptContext(schemes=["bcrypt"])
duraccion = 15

@router.post("/login", status_code=status.HTTP_200_OK)
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user = db_client.users.find_one({"name": form.username})
    if not user:
        raise HTTPException(status_code=400, detail="Usuario no encontrado")
    verifica_contra =encriptacion.verify(form.password, user["password"])

    if not verifica_contra:
        raise HTTPException(status_code=400, detail="ContraseNa Incorrecta")
    token = {
        "sub": user["name"],
        "exp": datetime.now(timezone.utc) + timedelta(minutes=duraccion)   }
    return {"access_token": jwt.encode(token,SECRET, algorithm=algoritmo), "token_type": "Bearer"}

def verificar_token(token: str = Depends(oauth2)):
    try:
        print(f"token recibido: {token}")
        payload = jwt.decode(token, SECRET, algorithms=[algoritmo])
        print(f"token decodificado {payload}")
        decode = payload.get("sub")
        print(payload)
        if not decode:
            raise HTTPException(status_code=400, detail="Token invalido")


    except Exception as e:
        print("🔥 ERROR COMPLETO:", repr(e))
        raise HTTPException(
            status_code=401,
            detail=f"Error JWT: {str(e)}")
    usuario = db_client.users.find_one({"name": decode})
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuario no encontrado")
    return  User(**esquema_usuario(usuario))

@router.get("/usuario", response_model=User, status_code=status.HTTP_200_OK)
async def usuario(user: User = Depends(verificar_token)):
    return user


#creamosnuestros usuarios
@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def add_user(user: Userdb):
    existe = db_client.users.find_one({"name": user.name})
    if existe:
        raise HTTPException(status_code=409, detail="Usuario ya existe")
    try:
        user_dict =dict(user)
        del user_dict["id"]
        user_dict["password"] = encriptacion.hash(user_dict["password"])

        insertar = db_client.users.insert_one(user_dict).inserted_id

        usuario = esquema_usuario(db_client.users.find_one({"_id": insertar}))
        return User(**usuario)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

#devolvemos los usuarios creados
@router.get("/", response_model=list[User], status_code=status.HTTP_200_OK)
async def list_usuarios():
    return esquema_usuarios(db_client.users.find())

#path
#consultamospor id de usuario
@router.get("/{id}", response_model=User, status_code=status.HTTP_200_OK)
async def consulta_usuario(id : str):
    usuario = db_client.users.find_one({"_id": ObjectId(id)})

    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Usuario no encontrado")

    return User(**esquema_usuario(usuario))

#borra un usuario
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_usuario(id: str):
    try:
        objet_id= ObjectId(id)
        eliminar = db_client.users.find_one({"_id": objet_id})
        if not eliminar:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        db_client.users.delete_one({"_id": objet_id})
    except:
        raise HTTPException(status_code=404, detail="Id invalido")

#actualizar datos de un usuario
@router.put("/", response_model=User, status_code=status.HTTP_200_OK)
async def update_user(user: User):
    
    user_dict =dict(user)
    id = user_dict.pop("id")
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=400,
            detail="ID de usuario no válido"
        )

    resultado = db_client.users.update_one(
        {"_id": ObjectId(id)},
        {"$set": user_dict}
    )
    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    nuevo_usuario = esquema_usuario(db_client.users.find_one({"_id": ObjectId(id)}))
    return User(**nuevo_usuario)