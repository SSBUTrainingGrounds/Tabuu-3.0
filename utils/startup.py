import os


def generate_files():
    """This generates some files that are required for the bot to run, if they aren't found."""
    files = [
        {
            "path": "./files/starboard.json",
            "content": '{ "emoji": "<:placeholder:1234>", "threshold": 5 }',
        },
        {
            "path": "./files/badwords.txt",
            "content": "badword1\nbadword2\nbadword3",
        },
        {
            "path": "./files/token.txt",
            "content": "your_token_here",
        },
    ]

    for file in files:
        if not os.path.exists(file["path"]):
            with open(file["path"], "w", encoding="utf-8") as f:
                f.write(file["content"])
