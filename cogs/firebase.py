from firebase_admin import firestore
from cogs.exception import InsufficientPointsError, MaxPointsError

DEFAULT_PROFILE = {
    "points": {},
    "is_blocked": False,
    "last_updated": firestore.SERVER_TIMESTAMP,
}


class Firestore:
    def __init__(self):
        self.db = firestore.AsyncClient()

        # Constants for firestore collection
        self.USER_COLLECTION = "users"
        self.ROLE_COLLECTION = "roles"
        self.TICKET_COLLECTION = "tickets"

    def get_user_doc_ref(self, username: str):
        return self.db.collection(self.USER_COLLECTION).document(username)

    async def get_user_doc(self, username: str):
        is_user_exist = await self.is_user_exist(username)
        if not is_user_exist:
            await self.create_user(username)

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

    async def add_points(self, username: str, points: int, role: str):
        user_doc = await self.get_user_doc(username)

        if role in user_doc["points"]:
            role_points = user_doc["points"][role]
            if role_points > 6:
                raise MaxPointsError(f"{username} already has 6 points from `{role}`")
            elif role_points + points > 6:
                raise MaxPointsError(
                    f"{username} can only receive maximum of {6 - role_points} points"
                )

        doc_ref = self.get_user_doc_ref(username)
        await doc_ref.update(
            {
                f"points.`{str(role)}`": firestore.Increment(points),
                "last_updated": firestore.SERVER_TIMESTAMP,
            }
        )

    async def minus_points(self, username: str, points: int, role: str):
        user_doc = await self.get_user_doc(username)

        if role not in user_doc["points"]:
            raise InsufficientPointsError(f"{username} has yet to receive any points from `{role}`")

        role_points = user_doc["points"][role]
        if role_points - points < 0:
            raise InsufficientPointsError(f"{username} only has `{role_points} points`")

        doc_ref = self.get_user_doc_ref(username)
        await doc_ref.update(
            {
                f"points.`{role}`": firestore.Increment(-points),
                "last_updated": firestore.SERVER_TIMESTAMP,
            }
        )

    async def block_user(self, username: str, is_blocked=False):
        await self.get_user_doc(username)
        doc_ref = self.get_user_doc_ref(username)
        await doc_ref.update({"is_blocked": is_blocked})

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
        role_doc = {"id": id, "name": name, "emoji": emoji}

        doc_ref = self.get_role_doc_ref(id)
        await doc_ref.set(role_doc)

    async def delete_role(self, id: str):
        doc_ref = self.get_role_doc_ref(id)
        await doc_ref.delete()

    async def get_all_roles(self):
        docs = self.db.collection(self.ROLE_COLLECTION).stream()
        result = []

        async for doc in docs:
            data = doc.to_dict()
            result.append(data)
        return result

    def get_ticket_doc_ref(self, ticket_id: str):
        return self.db.collection(self.TICKET_COLLECTION).document(ticket_id)

    async def register_ticket(
        self, ticket_id: str, is_root: bool, username: str, role_id: str
    ):
        ticket_doc = {
            "id": ticket_id,
            "last_updated": firestore.SERVER_TIMESTAMP,
            "is_available": True,
            "is_root": is_root,
            "username": username,
            "role_id": role_id,
        }

        doc_ref = self.get_ticket_doc_ref(ticket_id)
        await doc_ref.set(ticket_doc)

    async def is_ticket_exist(self, username: str):
        tickets = (
            self.db.collection(self.TICKET_COLLECTION)
            .where("username", "==", username)
            .where("is_available", "==", True)
        )
        docs = tickets.stream()
        data = [doc.to_dict() async for doc in docs]

        return True if data else False

    async def get_role_by_emoji(self, emoji: str):
        roles = (
            self.db.collection(self.ROLE_COLLECTION)
            .where("emoji", "==", emoji)
            .limit(1)
        )
        docs = roles.stream()
        data = [doc.to_dict() async for doc in docs]

        return None if not data else data[0]

    async def get_available_tickets(self):
        tickets = self.db.collection(self.TICKET_COLLECTION).where(
            "is_available", "==", True
        )

        docs = tickets.stream()

        return [doc.to_dict() async for doc in docs]

    async def delete_ticket(self, username: str):
        query = (
            self.db.collection(self.TICKET_COLLECTION)
            .where("is_root", "==", False)
            .where("is_available", "==", True)
            .where("username", "==", username)
        )
        tickets = await query.get()
        ticket_id = tickets[0].to_dict()["id"]

        ticket = self.get_ticket_doc_ref(ticket_id)
        return await ticket.update({"is_available": False})
