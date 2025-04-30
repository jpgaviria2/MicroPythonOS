


#import mip
#mip.install('github:miguelgrinberg/microdot/src/microdot/microdot.py')
# http://192.168.1.122/upload
# http://192.168.1.122/files//


from microdot import Microdot, Response
import os


# HTML template for the upload form
UPLOAD_FORM = '''
<!DOCTYPE html>
<html>
<head><title>File Manager</title></head>
<body>
    <h1>File Manager</h1>
    <p><a href="/files">View Files</a></p>
    <h2>Upload File</h2>
    <form method="POST" action="/upload" enctype="multipart/form-data">
        <input type="file" name="file">
        <input type="submit" value="Upload">
    </form>
</body>
</html>
'''

app = Microdot()

@app.route('/')
async def index(request):
    return '<a href="/files//">Files</a>'


@app.route('/files/<path:path>')
async def list_files(req, path=''):
    try:
        # Sanitize path to prevent directory traversal
        path = path.strip('/')
        if '..' in path:
            return Response('Invalid path', status_code=400)
        # Get directory contents
        full_path = '/' + path
        files = os.listdir(full_path) if path else os.listdir('/')
        html = '<h1>File Manager</h1><ul>'
        for f in files:
            link_path = f'{path}/{f}' if path else f
            html += f'<li><a href="/files/{link_path}">{f}</a> | <a href="/download/{link_path}">Download</a></li>'
        html += '</ul>'
        return Response(html, headers={'Content-Type': 'text/html'})
    except OSError as e:
        return Response(f'Error: {e}', status_code=500)


@app.route('/download/<path:path>')
async def download_file(req, path):
    try:
        full_path = '/' + path.strip('/')
        with open(full_path, 'rb') as f:
            content = f.read()  # Read in chunks for large files
        return Response(content, headers={
            'Content-Type': 'application/octet-stream',
            'Content-Disposition': f'attachment; filename="{path.split("/")[-1]}"'
        })
    except OSError as e:
        return Response(f'Error: {e}', status_code=404)



@app.route('/upload', methods=['GET'])
async def upload_form(req):
    return Response(UPLOAD_FORM, headers={'Content-Type': 'text/html'})



@app.route('/upload', methods=['POST'])
async def upload_file(req):
    try:
        # Check if form data contains a file
        if 'file' not in req.form or not req.files['file']['filename']:
            return Response('No file selected', status_code=400)
        # Get file details
        filename = req.files['file']['filename']
        file_content = req.files['file']['body']
        # Sanitize filename to prevent path traversal
        filename = filename.split('/')[-1].split('\\')[-1]
        if not filename:
            return Response('Invalid filename', status_code=400)
        # Save file to filesystem
        file_path = f'/{filename}'
        with open(file_path, 'wb') as f:
            f.write(file_content)  # Write in one go for small files
        # Free memory
        gc.collect()
        # Redirect to file listing
        return Response(status_code=302, headers={'Location': '/files'})
    except OSError as e:
        return Response(f'Error saving file: {e}', status_code=500)
    except MemoryError:
        return Response('File too large for available memory', status_code=507)



def startit():
	app.run(port=80)
	# http://192.168.1.115:5000


import _thread
_thread.start_new_thread(startit, ())

