from db_connection import db

print("Testing MySQL connection...")

if db.connect():
    print("SUCCESS: Connected to MySQL!")

    player_id = db.get_or_create_player("TestPlayer")

    if player_id:
        print(f"SUCCESS: Player inserted/found!")
        print(f"Player ID: {player_id}")
    else:
        print("FAILED: Could not insert player.")

    db.close()
else:
    print("FAILED: Could not connect to MySQL.")