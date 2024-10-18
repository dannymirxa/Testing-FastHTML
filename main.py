from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, EmailStr
import uvicorn
import database
import psycopg2.extras 
import json
from psycopg2 import Error
from passlib.context import CryptContext

app = FastAPI()

security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(BaseModel):
    Id : int
    Email : str
    Password : str
    Name : str

class UserCreate(BaseModel):
    Email : str
    Password : str
    Name : str

class Post(BaseModel):
    Id : int
    User_Id : int
    Image : str
    Caption : str

# class Comment(BaseModel):
#     Id : int
#     User_Id : int
#     Post_Id : int
#     Text : str

class Comment(BaseModel):
    Image : str
    Text : str

def get_db():
    return database.get_db_connection()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user_by_email(email: str):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM public.user WHERE email = %s", (email,))
    user = cur.fetchone()
    conn.close()
    return user

def get_postId_by_user_and_image(user: str, image: str):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""SELECT * FROM public.post 
                WHERE image = %s
                AND email = (SELECT email FROM public.user WHERE Email = %s)""", (image, user))
    post = cur.fetchone()
    conn.close()
    return post

@app.get("/login")
async def login(credentials: HTTPBasicCredentials = Depends(security)):
    user = get_user_by_email(credentials.username)
    if user is None or not verify_password(credentials.password, user['password']):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return {"message": "Login successful"}

@app.post("/userCreate/")
async def create_user(user: UserCreate) -> dict:
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        hashed_password = pwd_context.hash(user.Password)

        """{
            "Email": "danial@example.com",
            "Password": "danial1234",
            "Name": "danial"
        }"""
        cur.execute("""
            INSERT INTO public.user
            (email, password, name)
            VALUES(%s, %s, %s);
            """, (
                user.Email,
                hashed_password,
                user.Name
            ))
        conn.commit()
        return {"message": "User created successfully"}
    except Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
    finally:
        conn.close()

@app.get("/userByEmail/{email}")
async def read_user(email: str) -> dict:
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT name, email FROM public.user WHERE Email = %s", (email,))
    result = cur.fetchone()

    if not result:
        raise HTTPException(status_code=404, detail='User does not exist')
    conn.close()

    user = json.dumps(result, default=str)
    print(type(json.loads(user)))
    return json.loads(user)

@app.post("/uploadImage/")
async def upload_image(
        credentials: HTTPBasicCredentials = Depends(security),
        file: UploadFile = File(...),
        caption: str = Form(...)
    ):
    user = get_user_by_email(credentials.username)
    # print(credentials)
    if user is None or not verify_password(credentials.password, user['password']):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    file_location =  f"./{file.filename}"
    with open(file_location, "wb") as f:
        f.write(file.file.read())
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            INSERT INTO public.post (email, image, caption)
            VALUES (%s, %s, %s);
            """, (user['email'], file.filename, caption))
        conn.commit()
        return {"message": "Image uploaded and post created successfully"}
    except Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
    finally:
        conn.close()

@app.post("/postComment/")
async def create_post_comment(comment: Comment, 
        credentials: HTTPBasicCredentials = Depends(security)
        ):
    post = get_postId_by_user_and_image(credentials.username, comment.Image)

    # print(post)
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        """{
            "Image": "db exists.png",
            "Text": "string"
            }
            
        RealDictRow({'id': 1, 'user_id': 1, 'image': 'db exists.png', 'caption': 'db exists'})
        
        """
        
        cur.execute("""
            INSERT INTO public.comment
            (email, post_id, "text")
            VALUES(%s, %s, %s);
            """, (
                post['email'],
                post['id'],
                comment.Text
            ))
        conn.commit()
        return {"message": f"Post to Image {comment.Image} from User {credentials.username} created successfully"}
    except Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
    finally:
        conn.close()

@app.get("/postByEmail/{email}")
async def read_user(email: str) -> list:
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM public.post WHERE email = %s", (email,))
    result = cur.fetchall()

    if not result:
        raise HTTPException(status_code=404, detail='User does not exist')
    conn.close()

    posts = json.dumps(result, default=str)
    print(type(json.loads(posts)))
    return json.loads(posts)

@app.get("/commentsByImage/")
async def read_comments_by_image(credentials: HTTPBasicCredentials = Depends(security),
                    image: str = Form(...)
                    ):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    # print(credentials)
    # print(credentials.username)

    cur.execute("""select * from comment 
                    where email = %s
                    and id = (select id from post where 
                    email = %s and image = %s)""", 
                
                (credentials.username, credentials.username, image))
    
    result = cur.fetchall()

    if not result:
        raise HTTPException(status_code=404, detail='User does not exist')
    conn.close()

    comments = json.dumps(result, default=str)
    print(type(json.loads(comments)))
    return json.loads(comments)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

