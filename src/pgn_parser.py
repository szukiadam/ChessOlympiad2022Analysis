import chess.pgn
import json
import os
import csv

## TODO: Make it so that the headers are only added once !


def read_pgns_to_csv(pgn_csv_file):
    """
    Reads pgn files from the ./pgns folder and stores them in a csv file.
    """
    pgn_files = [file for file in os.listdir("./pgns") if ".pgn" in file]
    columns = [
        "event",
        "site",
        "date",
        "round",
        "white",
        "black",
        "result",
        "blackelo",
        "blackfideid",
        "blacktitle",
        "blackteam",
        "eco",
        "eventdate",
        "opening",
        "variation",
        "whiteelo",
        "whitefideid",
        "whitetitle",
        "whiteteam",
        "moves",
        "eventtype",
        "fen",
        "variant",
        "setup",
    ]

    for filename in pgn_files:
        file = open(f"./pgns/{filename}")

        result = []
        i = 0

        while True:
            i += 1
            try:
                game = chess.pgn.read_game(file)
                if game is None:
                    break
            except:
                continue

            headers = dict(game.headers)
            headers = {k.lower(): v for k, v in headers.items()}

            try:
                headers["moves"] = game.board().variation_san(game.mainline_moves())
            except:
                headers["moves"] = None

            result.append(headers)

        print(f"finished {filename}")

        for item in result[0].keys():
            if item not in columns:
                columns.append(item)

        with open(pgn_csv_file, "a", encoding="utf8", newline="") as csv_file:
            # Watch out because this will add the headers multiple times to the csv, not just once !
            writer = csv.DictWriter(csv_file, restval="-", fieldnames=columns)
            writer.writeheader()
            for item in result:
                writer.writerow(item)


if __name__ == "__main__":
    read_pgns_to_csv("olympiad2022.csv")
