from fastapi import Header
import jwt as JWT
from fastapi import HTTPException
from db.redis import RedisSesion
# dependency
async def login_required(Authorization:str = Header()):       
    try:
        _,Session_ID = RedisSesion.get_session(Authorization)
        if Session_ID is None:
            raise HTTPException(
                status_code=401,
                detail="Expired Session Error"
            )
    except JWT.ExpiredSignatureError:
        raise HTTPException(
                status_code=401,
                detail="Expired Signature Error"
            )
    except JWT.InvalidTokenError:
        raise HTTPException(
                status_code=401,
                detail="Invalid Token Error"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail= e
        )