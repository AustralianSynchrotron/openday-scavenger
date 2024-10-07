import json
import logging
import sys
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from openday_scavenger.api.db import get_db
from openday_scavenger.api.puzzles.schemas import PuzzleCreate, PuzzleUpdate
from openday_scavenger.api.puzzles.service import create, update

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

QUIZ_DEFAULT = {
    "treasure_as": {
        "solution": "beam,light,magnet,xray"
    }
}

def finder_upload_to_db(
    db_session: Annotated["Session", Depends(get_db)],
    quiz: dict
    ):
    
    for key, puzzle in quiz.items():        
        # try to create puzzle, if puzzle exists, update
        try:
            puzzle_in = PuzzleCreate(name=key, answer=puzzle['solution'], active=False)
            _ = create(db_session, puzzle_in)
            logger.info(f'uploaded {key} to db')
        except Exception as e:
            logger.info(f'Exception: {e}. Updating db')
            puzzle_in = PuzzleUpdate(name=key, answer=puzzle['solution'])
            _ = update(db_session, key, puzzle_in)
            logger.info(f'updated {key} in db')
    return


if __name__ == "__main__":
    # get puzzle entries from file and upload to db
    db_session = next(get_db())
    try:
        # make sure file exists
        filename = sys.argv[1]
        quiz = json.load(open(filename))
    except Exception as e:
        # otherwise load default quiz
        logger.info(f'Exception: {e}. Using default quiz')
        quiz = QUIZ_DEFAULT

    finder_upload_to_db(db_session, quiz)
    logger.info('Finished uploading finder puzzles to db')