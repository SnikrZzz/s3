import os
from flask import Flask, request
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import boto3
load_dotenv()
app = Flask(__name__)
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No se encontró ningún archivo', 400
    
    file = request.files['file']

    img_filename = secure_filename(file.filename)
    
    # Guardar el archivo en la ruta de destino
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], img_filename))
    upload_image_s3(img_filename)
    return 'Imagen recibida y guardada correctamente'

def upload_image_s3(image_name):
    img_path = os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], image_name))
    print(img_path)
    with open(img_path, 'rb') as f:
        image_data = f.read()

    try:
        s3_client = boto3.resource(
            "s3",
            aws_access_key_id = os.environ.get('ENV_AWS_ACCESS_KEY_ID'),
            aws_secret_access_key = os.environ.get('ENV_AWS_SECRET_ACCESS_KEY'),
            region_name = os.environ.get('ENV_AWS_REGION_NAME')
        )
        s3_client.Bucket(os.environ.get('ENV_AWS_S3_BUCKET_NAME')).put_object(Key = image_name, Body = image_data)
    except Exception as e:
        print(e)


def get_s3_image_url(image_name):
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('ENV_AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('ENV_AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('ENV_AWS_REGION_NAME')
        )
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': os.environ.get('ENV_AWS_S3_BUCKET_NAME'), 'Key': image_name},
            ExpiresIn=15
        )
        return response
    except Exception as e:
        print(e)
        return None


@app.route("/getImageLink/<imageName>")
def getImageLink(imageName):
    url = {'url': get_s3_image_url(imageName)}
    return url

if __name__ == '__main__':
    app.run(host="172.31.23.83")

