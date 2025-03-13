import json
import sqlite3
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import os

class PasswordDatabase:
    def __init__(self, db_path='passwords.db'):
        self.db_path = db_path
        self.key = self._get_or_create_key()
        self._init_db()

    def _get_or_create_key(self):
        if not os.path.exists('secret.key'):
            key = get_random_bytes(32)
            with open('secret.key', 'wb') as f:
                f.write(key)
        else:
            with open('secret.key', 'rb') as f:
                key = f.read()
        return key

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS passwords
                            (id INTEGER PRIMARY KEY,
                             website TEXT,
                             username TEXT,
                             password BLOB,
                             tags TEXT)''')

    def _encrypt(self, plaintext):
        cipher = AES.new(self.key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(plaintext.encode(), AES.block_size))
        return cipher.iv + ct_bytes

    def _decrypt(self, ciphertext):
        iv = ciphertext[:16]
        ct = ciphertext[16:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        return pt.decode()

    def save_password(self, website, username, password, tags):
        encrypted_pw = self._encrypt(password)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO passwords (website, username, password, tags) VALUES (?,?,?,?)',
                          (website, username, encrypted_pw, ','.join(tags)))

    def search_passwords(self, keyword):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM passwords WHERE website LIKE ? OR tags LIKE ?',
                          (f'%{keyword}%', f'%{keyword}%'))
            results = []
            for row in cursor.fetchall():
                decrypted_pw = self._decrypt(row[3])
                results.append({
                    'website': row[1],
                    'username': row[2],
                    'password': decrypted_pw,
                    'tags': row[4].split(',')
                })
            return results