# app/routes.py

from flask import render_template, request, send_from_directory
from flask_restful import Resource, reqparse
from werkzeug.utils import secure_filename
from app import app, api
from app.models import VideoInfo
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov'}
parser = reqparse.RequestParser()
parser.add_argument('user', type=str, help='User who uploaded the video', required=True)
parser.add_argument('position', type=str, help='Position of watermark', required=False)

video_info = VideoInfo()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class AudioExtraction(Resource):
    def post(self):
        args = parser.parse_args()
        user = args['user']

        file = request.files['video']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = f'app/static/{filename}'
            file.save(f'app/static/{filename}')

            # Perform audio extraction here
            audio_output_path = f'app/static/{filename.rsplit(".", 1)[0]}.mp3'
            video_clip = VideoFileClip(file_path)
            audio_clip = video_clip.audio
            audio_clip.write_audiofile(audio_output_path)
            audio_clip.close()


            video_info.insert_video_info(user, 'audio_extraction', filename)
            return {'message': 'Audio extraction successful', 'audio_file': audio_output_path}

        return {'error': 'Invalid file or format'}


class VideoWatermarking(Resource):
    def post(self):
        args = parser.parse_args()
        user = args['user']
        position = args['position']

        file = request.files['video']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = f'app/static/{filename}'
            file.save(f'app/static/{filename}')

            # Perform video watermarking here with the specified position

            watermark_text = "VideoAI"
            video_clip = VideoFileClip(file_path)
            txt_clip = TextClip(watermark_text, fontsize=70, color='white')
            if position == "center":
                txt_clip = txt_clip.set_position("center").set_duration(video_clip.duration)
            else:
                # Add more positions as needed
                txt_clip = txt_clip.set_position((0.05, 0.9)).set_duration(video_clip.duration)

            watermarked_clip = CompositeVideoClip([video_clip, txt_clip])

            watermarked_output_path = f'app/static/{filename.rsplit(".", 1)[0]}_watermarked.mp4'
            watermarked_clip.write_videofile(watermarked_output_path, codec='libx264', audio_codec='aac')
            watermarked_clip.close()

            video_info.insert_video_info(user, 'watermarking', filename)
            return {'message': 'Video watermarking successful', 'watermarked_video': watermarked_output_path}

        return {'error': 'Invalid file or format'}

api.add_resource(AudioExtraction, '/audio_extraction')
api.add_resource(VideoWatermarking, '/video_watermarking')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
