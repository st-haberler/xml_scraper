# import scr.tagger.flask_server
import scr.database.db_utils as db_utils

from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session

import scr.database.models as models

if __name__ == "__main__":
    r = db_utils.get_all_Gesetze()
    for g in r: 
        print(g.kurztitel, g.gesetzesnummer)


    engine = create_engine("sqlite:///test.db", echo=False)
    with Session(engine) as session:
        q = select(models.Document).where(models.Document.gesetzesnummer == 10000138)
        result = session.scalars(q).all()
        for r in result[5:6]: 
            print(r.artikelnummer)
            print(r.paragraphs[0].text)



