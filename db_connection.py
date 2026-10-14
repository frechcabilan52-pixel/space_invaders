import json
import os
import mysql.connector
from mysql.connector import Error


CONFIG_PATH = os.path.join(
    os.path.dirname(__file__),
    "db_config.json"
)


class Database:

    def __init__(self, config_path: str = CONFIG_PATH):
        self.config_path = config_path
        self.connection = None

    def _load_config(self) -> dict:
        with open(self.config_path, "r") as f:
            return json.load(f)

    def connect(self):
        """Open a database connection."""
        if self.connection and self.connection.is_connected():
            return True

        try:
            config = self._load_config()

            self.connection = mysql.connector.connect(
                host=config["host"],
                port=config.get("port", 3306),
                user=config["user"],
                password=config["password"],
                database=config["database"],
            )

            return True

        except Error as e:
            print(f"[Database] Connection failed: {e}")
            self.connection = None
            return False

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.connection = None


    # =====================================================
    # REGISTER PLAYER WITH USERNAME + PASSWORD
    # =====================================================

    def register_player(
        self,
        username: str,
        password: str
    ) -> int | None:

        if not self.connect():
            return None

        cursor = self.connection.cursor()

        try:

            cursor.execute(
                """
                SELECT player_id
                FROM players
                WHERE username = %s
                """,
                (username,)
            )

            if cursor.fetchone():
                print("[Database] Username already exists.")
                return None

            cursor.execute(
                """
                INSERT INTO players
                (username, password)
                VALUES (%s, %s)
                """,
                (username, password)
            )

            self.connection.commit()

            print(
                f"[Database] Player '{username}' registered."
            )

            return cursor.lastrowid

        except Error as e:

            print(
                f"[Database] register_player failed: {e}"
            )

            self.connection.rollback()
            return None

        finally:
            cursor.close()


    # =====================================================
    # LOGIN WITH USERNAME + PASSWORD
    # =====================================================

    def get_player(
        self,
        username: str,
        password: str
    ):

        if not self.connect():
            return None

        cursor = self.connection.cursor()

        try:

            cursor.execute(
                """
                SELECT
                    player_id,
                    username,
                    created_at
                FROM players
                WHERE username = %s
                AND password = %s
                """,
                (username, password)
            )

            return cursor.fetchone()

        except Error as e:

            print(
                f"[Database] get_player failed: {e}"
            )

            return None

        finally:
            cursor.close()


    # =====================================================
    # GET OR CREATE PLAYER
    # =====================================================

    def get_or_create_player(
        self,
        username: str
    ) -> int | None:

        if not self.connect():
            return None

        cursor = self.connection.cursor()

        try:

            cursor.execute(
                """
                SELECT player_id
                FROM players
                WHERE username = %s
                """,
                (username,)
            )

            row = cursor.fetchone()

            if row:
                return row[0]

            cursor.execute(
                """
                INSERT INTO players (username)
                VALUES (%s)
                """,
                (username,)
            )

            self.connection.commit()

            return cursor.lastrowid

        except Error as e:

            print(
                f"[Database] get_or_create_player failed: {e}"
            )

            return None

        finally:
            cursor.close()


    # =====================================================
    # UPDATE PLAYER PROFILE
    # =====================================================

    def update_player_profile(
        self,
        old_username: str,
        new_username: str
    ) -> bool:

        if not self.connect():
            return False

        cursor = self.connection.cursor()

        try:

            cursor.execute(
                """
                UPDATE players
                SET username = %s
                WHERE username = %s
                """,
                (new_username, old_username)
            )

            self.connection.commit()

            if cursor.rowcount > 0:

                print(
                    f"[Database] Username updated: "
                    f"{old_username} -> {new_username}"
                )

                return True

            print("[Database] Player not found.")
            return False

        except Error as e:

            print(
                f"[Database] update_player_profile failed: {e}"
            )

            self.connection.rollback()
            return False

        finally:
            cursor.close()


    # =====================================================
    # DELETE PLAYER
    # =====================================================

    def delete_player(
        self,
        username: str
    ) -> bool:

        if not self.connect():
            return False

        cursor = self.connection.cursor()

        try:

            cursor.execute(
                """
                SELECT player_id
                FROM players
                WHERE username = %s
                """,
                (username,)
            )

            row = cursor.fetchone()

            if row is None:
                print("[Database] Player not found.")
                return False

            player_id = row[0]

            cursor.execute(
                """
                DELETE FROM scores
                WHERE player_id = %s
                """,
                (player_id,)
            )

            cursor.execute(
                """
                DELETE FROM players
                WHERE player_id = %s
                """,
                (player_id,)
            )

            self.connection.commit()

            print(
                f"[Database] Player '{username}' deleted."
            )

            return True

        except Error as e:

            print(
                f"[Database] delete_player failed: {e}"
            )

            self.connection.rollback()
            return False

        finally:
            cursor.close()


    # =====================================================
    # SAVE SCORE
    # =====================================================

    def save_score(
        self,
        username: str,
        score: int
    ) -> bool:

        player_id = self.get_or_create_player(username)

        if player_id is None:
            return False

        cursor = self.connection.cursor()

        try:

            cursor.execute(
                """
                INSERT INTO scores
                (player_id, score)
                VALUES (%s, %s)
                """,
                (player_id, score)
            )

            self.connection.commit()

            return True

        except Error as e:

            print(
                f"[Database] save_score failed: {e}"
            )

            self.connection.rollback()
            return False

        finally:
            cursor.close()


    # =====================================================
    # LEADERBOARD
    # =====================================================

    def get_top_scores(
        self,
        limit: int = 10
    ) -> list[tuple]:

        if not self.connect():
            return []

        cursor = self.connection.cursor()

        try:

            cursor.execute(
                """
                SELECT
                    p.username,
                    s.score,
                    s.played_at
                FROM scores s
                JOIN players p
                    ON p.player_id = s.player_id
                WHERE s.score_id = (
                    SELECT s2.score_id
                    FROM scores s2
                    WHERE s2.player_id = s.player_id
                    ORDER BY
                        s2.score DESC,
                        s2.played_at DESC,
                        s2.score_id DESC
                    LIMIT 1
                )
                ORDER BY
                    s.score DESC,
                    s.played_at DESC
                LIMIT %s
                """,
                (limit,)
            )

            return cursor.fetchall()

        except Error as e:

            print(
                f"[Database] get_top_scores failed: {e}"
            )

            return []

        finally:
            cursor.close()


db = Database()