
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