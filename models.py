# app/models.py

from app import mongo
from datetime import datetime

class VideoInfo:
    def insert_video_info(self, user, task, filename):
        mongo.db.video_info.insert_one({
            'user': user,
            'task': task,
            'filename': filename,
            'timestamp': datetime.utcnow()
        })
