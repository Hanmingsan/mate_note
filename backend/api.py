import fastapi
import db

app = fastapi.FastAPI()

@app.get("/mates")
def query_mates(name: str):
    data = None
    try:
        data = db.sm.query_mate_by_name(name)[0]
    except IndexError:
        return {"message": "mate not found in database"}
    except Exception as e:
        return {"message": f"error {e} happened"}
    else:
        return {"id":          data[0],
                "name":        data[1],
                "tel":         data[2],
                "wechat_id":   data[3],
                "qq_id":       data[4],
                "motto":       data[5],
                "comment":     data[6],
                "photo_url":   data[7]
                }

@app.post("/add_mate")
def add_mate(name: str,
             comment: str,
             tel: str = None,
             wechat_id: str = None,
             qq_id: str = None,
             personal_motto: str = None,
             photo_url: str = None
            ):
    status = db.cm.create_mate(name, comment, tel, wechat_id, qq_id, personal_motto, photo_url)
    return {"status": f"{str(status)}"}

@app.post("/delete_mate")
def delete_mate(name: str):
    status = db.dm.delete_mate_by_name(name)
    return {"status": f"{str{status}}"}
