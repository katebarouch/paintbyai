import svgwrite
from svgwrite import Drawing, path
from sklearn.cluster import KMeans
import numpy as np
import openai
import requests
from PIL import Image
import io
from svgpathtools import parse_path, Line, QuadraticBezier, svg2paths2
from dotenv import load_dotenv
import os
load_dotenv(".gitignore/secrets.sh")

def dall_e():
    # define OpenAI key
    api_key = os.getenv("OPENAI_API_KEY")
    openai.api_key = api_key

    # text prompt
    answer = input("What would you like to paint today?")
    prompt = (f"a watercolor painting of {answer}")
    # prompt = answer

    # generate an image
    response = openai.Image.create(
        prompt=prompt,
        model="image-alpha-001",
        size="1024x1024",
        response_format="url"
    )
    print(response)
    return response

def dalle(prompt):
    # define OpenAI key
    api_key = os.getenv("OPENAI_API_KEY")
    openai.api_key = api_key

    # prompt = answer

    # generate an image
    response = openai.Image.create(
        prompt=prompt,
        model="image-alpha-001",
        size="1024x1024",
        response_format="url"
    )
    print(response)
    return response

def generate_image(api_url, painting_id):
    # Extract the URL from the response dictionary
    url = api_url['data'][0]['url']

    # Make a request to the DALL·E API to get the image data
    response = requests.get(url)
    response.raise_for_status()
    image_data = response.content

    # Load the image data into a Pillow image object
    image = Image.open(io.BytesIO(image_data))

    # Save the image as a JPEG file
    output_file = f'static/images/{painting_id}dalle.jpg'
    image.save(output_file, 'JPEG')

    print(f"Image saved as {output_file}")
    return output_file

def vectorize(image, painting_id):
    response = requests.post(
        'https://vectorizer.ai/api/v1/vectorize',
        files={'image': open(image,"rb")},
        # data={
        #     # TODO: Add more upload options here
        # },
        headers={
            'Authorization':
            'Basic dmtrZm1sY2ZqOGI1aDdrOmdsdXBkcmVpNmw0am4wMXJtODJoZ2QxMnEyNjUwYWhmZmQ0b3ZncGd2cm4ydGFka3VvcDc='
        },
    )
    if response.status_code == requests.codes.ok:
        # Save result
        with open(f'static/images/{painting_id}vectorized.svg', 'wb') as out:
            out.write(response.content)


    else:
        print("Error:", response.status_code, response.text)

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb_color):
    return '#%02x%02x%02x' % rgb_color

def get_closest_color(color, colors):
    if isinstance(color, str):
        color = hex_to_rgb(color)
    color = np.array(color)
    colors = np.array(colors)
    distances = np.sqrt(np.sum((colors - color) ** 2, axis=1))
    closest_index = np.argmin(distances)
    closest_color = colors[closest_index]
    return closest_color

def replace_fill_colors(svg_file, num_colors, output_file):
    drawing = svgwrite.Drawing(filename=output_file)

    fill_colors = []
    # Load SVG paths and attributes
    paths, attributes, svg_attributes = svg2paths2(svg_file)
    # Extract fill colors from attributes
    for index in range(len(paths)):
        path_attributes = attributes[index]
        if 'fill' in path_attributes:
            fill_colors.append(path_attributes['fill'])

    # Convert fill colors to RGB format
    fill_colors_rgb = [hex_to_rgb(color) for color in fill_colors]
    fill_colors_rgb = np.array(fill_colors_rgb)

    # Perform K-means clustering to find centroid colors
    kmeans = KMeans(n_clusters=num_colors)
    kmeans.fit(fill_colors_rgb)
    cluster_centers = kmeans.cluster_centers_

    new_colors = []

    for index, path in enumerate(paths):
        path_attributes = attributes[index]

        if 'fill' in path_attributes and 'd' in path_attributes:
            fill_color = path_attributes['fill']

            if fill_color in fill_colors:
                fill_color_index = fill_colors.index(fill_color)

                if fill_color_index < len(cluster_centers):
                    new_color = cluster_centers[fill_color_index]
                    new_color_hex = rgb_to_hex(tuple(int(c) for c in new_color))

                    d = " ".join(path_attributes['d'].split())
                    new_path = svgwrite.path.Path(d=d, fill=new_color_hex)
                    drawing.add(new_path)
                    new_colors.append(new_color_hex)
                else:
                    closest_color = get_closest_color(fill_color, cluster_centers)
                    closest_color_hex = rgb_to_hex(tuple(int(c) for c in closest_color))

                    d = " ".join(path_attributes['d'].split())
                    new_path = svgwrite.path.Path(d=d, fill=closest_color_hex)
                    drawing.add(new_path)
                    new_colors.append(closest_color_hex)
            else:
                closest_color = get_closest_color(fill_color, cluster_centers)
                closest_color_hex = rgb_to_hex(tuple(int(c) for c in closest_color))

                d = " ".join(path_attributes['d'].split())
                new_path = svgwrite.path.Path(d=d, fill=closest_color_hex)
                drawing.add(new_path)
                new_colors.append(closest_color_hex)


        elif 'stroke' in path_attributes and 'd' in path_attributes:
            stroke_color = path_attributes['stroke']
            if stroke_color in fill_colors:
                stroke_color_index = fill_colors.index(stroke_color)
                if stroke_color_index < len(cluster_centers):
                    new_color = cluster_centers[stroke_color_index]
                    new_color_hex = rgb_to_hex(tuple(int(c) for c in new_color))
                    new_path = svgwrite.path.Path(d=" ".join(path_attributes['d'].split()), stroke=new_color_hex, fill='none')
                    drawing.add(new_path)
                    new_colors.append(new_color_hex)
                else:
                    closest_color = get_closest_color(stroke_color, cluster_centers)
                    closest_color_hex = rgb_to_hex(tuple(int(c) for c in closest_color))
                    new_path = svgwrite.path.Path(d=" ".join(path_attributes['d'].split()), stroke=closest_color_hex, fill='none')
                    drawing.add(new_path)
                    new_colors.append(closest_color_hex)
            else:

                closest_color = get_closest_color(stroke_color, cluster_centers)
                closest_color_hex = rgb_to_hex(tuple(int(c) for c in closest_color))
                new_path = svgwrite.path.Path(d=" ".join(path_attributes['d'].split()), stroke=closest_color_hex, fill='none')
                drawing.add(new_path)
                new_colors.append(closest_color_hex)

    drawing.saveas(output_file)
    return new_colors

def merge_neighboring_paths(paths, attributes):
    merged_paths = []
    merged_attributes = []

    for index, path in enumerate(paths):
        path_attributes = attributes[index]

        if 'fill' in path_attributes and 'd' in path_attributes:
            fill_color = path_attributes['fill']

            # Check if the current path has the same fill color as the previous merged path
            if merged_paths and merged_attributes[-1]['fill'] == fill_color:
                # Append the current path's 'd' attribute to the previous merged path's 'd' attribute
                merged_attributes[-1]['d'] += " " + path_attributes['d']
            else:
                # Add a new merged path with the current path's attributes
                merged_paths.append(path)
                merged_attributes.append(path_attributes)

    return merged_paths, merged_attributes

def remove_inner_segments(paths, attributes):
    cleaned_paths = []
    cleaned_attributes = []
    centers = []

    for path, attribute in zip(paths, attributes):
        path_obj = parse_path(path)
        bbox = path_obj.bbox()
        center = (bbox[0] + bbox[2]) / 2 + (bbox[1] + bbox[3]) / 2 * 1j

        intersection_points = []
        contributing_segments = []

        for segment in path_obj:
            line = Line(center, segment.point(0.5))

            if segment is not None and segment.intersect(line):

                intersection = segment.intersect(line)
                if intersection is not None:
                    for point, _ in intersection:
                        if isinstance(segment, Line):
                            intersection_points.append(complex(point.real, point.imag))
                        elif isinstance(segment, QuadraticBezier):
                            intersection_points.append(complex(point[0].real, point[0].imag))

                    contributing_segments.append(segment)

        intersection_points.sort(key=lambda p: abs(p - center))

        if intersection_points:
            first_intersection_index = path_obj.point_to_segment_index(intersection_points[0])
            subpaths = path_obj.split(first_intersection_index)

            final_path = subpaths[0]
            for subpath in subpaths[1:]:
                final_path += subpath
        else:
            final_path = path_obj

        cleaned_paths.append(str(final_path).replace("Path(", "").replace(")", ""))
        cleaned_attributes.append(attribute)
        centers.append(center)

    return cleaned_paths, cleaned_attributes, centers


def replace_fill_colors_black_lines(svg_file, output2_file):
    attempt_count = 0
    max_attempts = 5

    while attempt_count < max_attempts:
        try:
            paths, attributes, svg_attributes = svg2paths2(svg_file)

            # Merge neighboring paths with the same fill color
            paths, attributes = merge_neighboring_paths(paths, attributes)

            # Remove any unnecessary path segments in the center of the path
            paths, attributes, centers = remove_inner_segments(paths, attributes)

            drawing = Drawing(output2_file, viewBox="0 0 1024 1024")

            # Save the drawing as an SVG file
            drawing.saveas(output2_file)

            # Dictionary to store hex codes and their corresponding numbers
            color_dict = {}

            for index in range(len(paths)):
                path_str = paths[index]
                path_attributes = attributes[index]

                # Create a group element
                group = drawing.add(drawing.g())

                if 'fill' in path_attributes and 'd' in path_attributes:
                    # Get the fill color
                    fill_color = path_attributes['fill']

                    # Clean up the 'd' attribute
                    d = " ".join(path_attributes['d'].split())

                    # Create a new path with the specified attributes
                    new_path = path.Path(
                        d=d,
                        fill=fill_color,
                        fill_opacity=0.15,
                        stroke=fill_color,
                        stroke_opacity=0.25,
                        stroke_width=1.25,
                    )

                    # Add the new path to the drawing
                    drawing.add(new_path)

                    # Assign number to the fill color or reuse existing number
                    if fill_color not in color_dict:
                        color_dict[fill_color] = len(color_dict) + 1
                    number = color_dict[fill_color]

                    # Find the first two segments of the path
                    segments = parse_path(d)
                    segment1 = segments[0]
                    segment2 = segments[1]

                    # Calculate the midpoint of the first two segments
                    midpoint = (segment1.point(0.5) + segment2.point(0.5)) / 2

                    # Add the text element above the path at the midpoint
                    text = drawing.text(
                        fill=fill_color,
                        insert=(midpoint.real, midpoint.imag - 1),
                        text=str(number),
                    )
                    text['font-size'] = "7px"
                    text['text-anchor'] = 'middle'
                    text['dominant-baseline'] = 'central'  # Center the text horizontally
                    group.add(text)

            # Save the drawing as an SVG file
            drawing.saveas(output2_file)

            # Print the color dictionary
            print("Color Dictionary:")
            for color, number in color_dict.items():
                print(f"Hex Code: {color} - Number: {number}")

            return color_dict

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            attempt_count += 1

    print("Max attempts reached. Function failed.")
    return None

    

# def main():
#     response = dall_e()
#     generate_image(response)
#     vectorize('generated_image.jpg')
#     svg_file = 'result.svg'
#     num_colors = 20
#     output_file = 'output.svg'
#     output2_file = 'output2.svg'


#     new_colors = replace_fill_colors(svg_file, num_colors, output_file)
#     replace_fill_colors_black_lines(output_file, output2_file)

#     print("SVG file has been successfully created.")
#     print("Number of unique colors in the image:", len(set(new_colors)))

def create_paint_by_numbers(prompt, num_colors, painting_id):

    prompt = prompt
    response = dalle(prompt)
    print('response')
    output_file = generate_image(response, painting_id)
    print(output_file)
    vectorize(f'static/images/{painting_id}dalle.jpg', painting_id)
    num_colors = num_colors

    new_colors = replace_fill_colors(f'static/images/{painting_id}vectorized.svg', num_colors, output_file)
    color_dict = replace_fill_colors_black_lines(output_file, f'static/images/{painting_id}final.svg')

    return color_dict

