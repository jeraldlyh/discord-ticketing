from firebase_admin import firestore


DEFAULT_PROFILE = {
    "points": 0,
    "is_blocked": False,
    "last_updated": firestore.SERVER_TIMESTAMP
}

class Firestore():
    def __init__(self):
        self.db = firestore.AsyncClient()

        # Constants for firestore collection
        self.USER_COLLECTION = "users"
        self.ROLE_COLLECTION = "roles"

    def get_user_doc_ref(self, username: str):
        return self.db.collection(self.USER_COLLECTION).document(username)

    async def get_user_doc(self, username: str):
        doc_ref = self.get_user_doc_ref(username)
        doc = await doc_ref.get()

        return doc.to_dict()

    async def is_user_exist(self, username: str):
        doc_ref = self.get_user_doc_ref(username)
        doc = await doc_ref.get()

        return doc.exists
    
    async def create_user(self, username: str):
        doc_ref = self.get_user_doc_ref(username)
        await doc_ref.set(DEFAULT_PROFILE)

    async def add_points(self, username: str, points: int):
        if (points < 1 or points > 5):
            raise SyntaxError("Points must be within 1 to 5")

        doc_ref = self.get_user_doc_ref(username)
        await doc_ref.update({
            "points": firestore.Increment(points),
            "last_updated": firestore.SERVER_TIMESTAMP
        })

    async def minus_points(self, username: str, points: int):
        if (points < 1 or points > 5):
            raise SyntaxError("Points must be within 1 to 5")

        user_doc = await self.get_user_doc(username)
        if (user_doc["points"] == 0):
            raise ValueError("User has insufficient points")

        doc_ref = self.get_user_doc_ref(username)
        await doc_ref.update({
            "points": firestore.Increment(-points),
            "last_updated": firestore.SERVER_TIMESTAMP
        })
    
    async def block_user(self, username: str, is_blocked=False):
        doc_ref = self.get_user_doc_ref(username)
        await doc_ref.update({
            "is_blocked": is_blocked
        })
    
    async def get_all_users(self):
        docs = self.db.collection(self.USER_COLLECTION).stream()
        result = []

        async for doc in docs:
            data = doc.to_dict()
            data["username"] = doc.id
            result.append(data)

        return sorted(result, key=lambda x: x["points"])
    
    def get_role_doc_ref(self, role_id: str):
        return self.db.collection(self.ROLE_COLLECTION).document(role_id)

    async def get_role_doc(self, role_id: str):
        doc_ref = self.get_role_doc_ref(role_id)
        doc = await doc_ref.get()

        return doc.to_dict()
    
    async def create_role(self, id: str, name: str, emoji: str):
        role_doc = {
            "id": id,
            "name": name,
            "emoji": emoji
        }

        doc_ref = self.get_role_doc_ref(id)
        await doc_ref.set(role_doc)
    
    async def delete_role(self, id: str):
        doc_ref = self.get_role_doc_ref(id)
        await doc_ref.delete()


