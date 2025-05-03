import pickle
from pathlib import Path
import bcrypt


names=["Karabo Woto","Thabang Motse"]
usernames=["kwoto","tmotse"]
passwords=['123abc','thabang02']

hashed_passwords = [bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode() for pw in passwords]

file_path=Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("wb") as file:
    pickle.dump(hashed_passwords, file)