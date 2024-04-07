from flask import Flask, render_template, request, redirect, url_for, send_file
from PIL import Image, ImageFilter, ImageEnhance
import io
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['image']
    
    if file.filename == '':
        return redirect(url_for('index'))
    
    try:
        img = Image.open(file)
        img.save("static/original.jpg")
    except OSError as e:
        print("Error:", e)
        return redirect(url_for('index'))
    
    return redirect(url_for('edit'))

@app.route('/edit')
def edit():
    return render_template('edit.html', original="static/original.jpg")

def apply_color_adjustment_factor(image, adjustment_factor):
    enhancer = ImageEnhance.Color(image)
    img = enhancer.enhance(adjustment_factor)
    return img

def apply_crop(image, crop_values):                                      
    if crop_values.strip():  
        try:
            top, right, bottom, left = map(int, crop_values.split(','))
            new_width = image.width - left - right
            new_height = image.height - top - bottom
            img = image.crop((left, top, left + new_width, top + new_height))
            return img
        except ValueError:
            print("Invalid crop_coords format")
            return image
    else:
        return image

@app.route('/filter', methods=['POST'])
def filter():
    try:
        img = Image.open("static/original.jpg")
        
        rotate_angle = int(request.form['rotate_angle'])
        blur_radius = int(request.form['blur_radius'])
        brightness_factor = float(request.form['brightness_factor'])
        saturation_factor = float(request.form['saturation_factor'])
        crop_coords = request.form['crop_coords']
        adjustment_factor = float(request.form['adjustment_factor'])

        img = apply_crop(img, crop_coords)
        img = apply_color_adjustment_factor(img, adjustment_factor)

        if rotate_angle != 0:
            img = img.rotate(rotate_angle)
            
        if blur_radius != 0:
            img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
            
        if brightness_factor != 1.0:
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(brightness_factor)
            
        if saturation_factor != 1.0:
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(saturation_factor)
            
        img.save("static/filtered.jpg")
        
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        return render_template('edit.html', processed_image_data=img_bytes.getvalue(), original="static/original.jpg", filtered="static/filtered.jpg")
    
    except Exception as e:
        print("Error:", e)
        return redirect(url_for('edit'))

# Route to reset the filtered image to its original state
@app.route('/reset', methods=['POST'])
def reset():
    try:
        # Generate a new URL for the original image
        original_url = url_for('static', filename='original.jpg')
        return original_url
    
    except Exception as e:
        print("Error resetting image:", e)
        return redirect(url_for('edit'))



@app.route('/success', methods=['GET'])
def success():
    return render_template('success.html')

@app.route('/download_filtered', methods=['GET'])
def download_filtered():
    try:
        file_path = "static/filtered.jpg"
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        print("Error:", e)
        return redirect(url_for('edit'))

# Add routes for other pages if needed
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/crop')
def crop():
    return render_template('crop.html')

@app.route('/rotation')
def rotation():
    return render_template('rotation.html')

@app.route('/blur')
def blur():
    return render_template('blur.html')

@app.route('/brightness')
def brightness():
    return render_template('brightness.html')

@app.route('/saturation')
def saturation():
    return render_template('saturation.html')

@app.route('/color')
def color():
    return render_template('color.html')

if __name__ == '__main__':
    app.run(debug=True)
