from flask import Flask, render_template_string, redirect, url_for, request
import os
import xml.etree.ElementTree as ET

app = Flask(__name__)
ARCHIMATE_FOLDER = "archimate_files"

def strip_ns(tag):
    return tag.split("}")[-1] if "}" in tag else tag

def find_all_elements(root):
    elements = []
    relationships = []

    for elem in root.iter():
        tag = strip_ns(elem.tag)
        if tag == "element":
            xsi_type = elem.attrib.get("{http://www.w3.org/2001/XMLSchema-instance}type", "Unknown")
            data = {
                "id": elem.attrib.get("id"),
                "name": elem.attrib.get("name", "[no name]"),
                "type": xsi_type,
                "source": elem.attrib.get("source"),
                "target": elem.attrib.get("target")
            }
            if "Relationship" in xsi_type:
                relationships.append(data)
            else:
                elements.append(data)
    return elements, relationships

def parse_diagram_objects(parent_elem):
    boxes = []
    for child in parent_elem.findall("./child"):
        bounds = child.find(".//bounds")
        if bounds is None:
            continue

        box = {
            "id": child.attrib.get("id"),
            "element_id": child.attrib.get("archimateElement"),
            "x": int(bounds.attrib.get("x", 0)),
            "y": int(bounds.attrib.get("y", 0)),
            "width": int(bounds.attrib.get("width", 120)),
            "height": int(bounds.attrib.get("height", 55)),
            "children": parse_diagram_objects(child)  # recursion
        }
        boxes.append(box)
    return boxes

def flatten_boxes(boxes, offset_x=0, offset_y=0):
    flat = []
    for box in boxes:
        abs_x = offset_x + box["x"]
        abs_y = offset_y + box["y"]
        flat_box = {
            "id": box["id"],
            "element_id": box["element_id"],
            "x": abs_x,
            "y": abs_y,
            "width": box["width"],
            "height": box["height"]
        }
        flat.append(flat_box)
        flat.extend(flatten_boxes(box["children"], abs_x, abs_y))
    return flat

def get_connection_points(src, tgt):
    src_cx = src["x"] + src["width"] / 2
    src_cy = src["y"] + src["height"] / 2
    tgt_cx = tgt["x"] + tgt["width"] / 2
    tgt_cy = tgt["y"] + tgt["height"] / 2

    if abs(src_cx - tgt_cx) > abs(src_cy - tgt_cy):
        x1 = src["x"] + (src_cx < tgt_cx) * src["width"]
        y1 = src_cy
        x2 = tgt["x"] + (src_cx > tgt_cx) * tgt["width"]
        y2 = tgt_cy
    else:
        x1 = src_cx
        y1 = src["y"] + (src_cy < tgt_cy) * src["height"]
        x2 = tgt_cx
        y2 = tgt["y"] + (src_cy > tgt_cy) * tgt["height"]

    return x1, y1, x2, y2

@app.route("/", methods=["GET", "POST"])
def index():
    files = sorted([f for f in os.listdir(ARCHIMATE_FOLDER) if f.endswith(".archimate")])
    if request.method == "POST":
        selected = request.form.get("filename")
        return redirect(url_for("view_file", filename=selected))
    return render_template_string("""
        <h1>ArchiMate Viewer</h1>
        <form method="post">
            <label>Select .archimate file:</label>
            <select name="filename">
                {% for f in files %}
                    <option value="{{ f }}">{{ f }}</option>
                {% endfor %}
            </select>
            <button type="submit">View</button>
        </form>
    """, files=files)

@app.route("/view/<filename>")
def view_file(filename):
    path = os.path.join(ARCHIMATE_FOLDER, filename)
    if not os.path.exists(path):
        return f"<h2>File not found: {filename}</h2>"

    try:
        with open(path, "r", encoding="utf-8") as file:
            tree = ET.parse(file)
            root = tree.getroot()

        elements, relationships = find_all_elements(root)
        element_names = {e['id']: e['name'] for e in elements}
        diagrams = []

        for diagram in root.iter():
            if strip_ns(diagram.tag) == "element" and diagram.attrib.get("{http://www.w3.org/2001/XMLSchema-instance}type") == "archimate:ArchimateDiagramModel":
                view_name = diagram.attrib.get("name", "Unnamed View")
                nested_boxes = parse_diagram_objects(diagram)
                flat_boxes = flatten_boxes(nested_boxes)

                box_map = {box["id"]: box for box in flat_boxes}
                arrows = []

                for child in diagram.findall(".//sourceConnection"):
                    src = box_map.get(child.attrib.get("source"))
                    tgt = box_map.get(child.attrib.get("target"))
                    if src and tgt:
                        x1, y1, x2, y2 = get_connection_points(src, tgt)
                        arrows.append((x1, y1, x2, y2))

                max_x = max((b["x"] + b["width"] for b in flat_boxes), default=800)
                max_y = max((b["y"] + b["height"] for b in flat_boxes), default=600)

                diagrams.append({
                    "name": view_name,
                    "boxes": flat_boxes,
                    "arrows": arrows,
                    "element_names": element_names,
                    "max_x": max_x + 100,
                    "max_y": max_y + 100
                })

        return render_template_string("""
        <h1>Viewing: {{ filename }}</h1>
        <a href="{{ url_for('index') }}">← Back to file list</a>
        {% for d in diagrams %}
            <h3>📊 Diagram: {{ d.name }}</h3>
            <svg width="{{ d.max_x }}" height="{{ d.max_y }}" style="border:1px solid #ccc;">
                {% for box in d.boxes %}
                    <rect x="{{ box.x }}" y="{{ box.y }}" width="{{ box.width }}" height="{{ box.height }}"
                          fill="#e0f7fa" stroke="#00796b" stroke-width="2"/>
                    <text x="{{ box.x + 5 }}" y="{{ box.y + 15 }}" font-size="11" fill="black">
                        {{ d.element_names.get(box.element_id, box.element_id) }}
                    </text>
                {% endfor %}
                {% for x1, y1, x2, y2 in d.arrows %}
                    <line x1="{{ x1 }}" y1="{{ y1 }}" x2="{{ x2 }}" y2="{{ y2 }}"
                          stroke="red" stroke-width="2" marker-end="url(#arrow)"/>
                {% endfor %}
                <defs>
                    <marker id="arrow" markerWidth="10" markerHeight="10" refX="5" refY="3"
                            orient="auto" markerUnits="strokeWidth">
                        <path d="M0,0 L0,6 L9,3 z" fill="red"/>
                    </marker>
                </defs>
            </svg>
        {% endfor %}
        """, filename=filename, diagrams=diagrams, element_names=element_names)

    except Exception as e:
        return f"<h2>Error parsing {filename}: {str(e)}</h2>"

if __name__ == "__main__":
    app.run(debug=True)
