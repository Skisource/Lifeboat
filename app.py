from pathlib import Path

from flask import Flask, render_template, request, send_file

from services import excel_parser, pdf_generator

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max upload

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)


@app.route("/")
def index():
    """Serve main page with upload form."""
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    """Accept two xlsx files, cross-reference, and return PDF."""
    if "familiarisation" not in request.files or "pob" not in request.files:
        return {"error": "Both files are required"}, 400

    fam_file = request.files["familiarisation"]
    pob_file = request.files["pob"]

    if not fam_file.filename or not pob_file.filename:
        return {"error": "Both files are required"}, 400

    if not fam_file.filename.endswith(".xlsx") or not pob_file.filename.endswith(
        ".xlsx"
    ):
        return {"error": "Only .xlsx files are accepted"}, 400

    try:
        fam_names = excel_parser.parse_familiarisation_list(fam_file)
        pob_names = excel_parser.parse_pob_list(pob_file)

        matched_personnel = excel_parser.cross_reference(fam_names, pob_names)

        if not matched_personnel:
            return {"error": "No matching personnel found on board"}, 404

        vessel_name = request.form.get("vessel_name", "")
        pdf_path = pdf_generator.generate_pdf(matched_personnel, vessel_name)

        return send_file(
            pdf_path,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="lifeboat_familiarisation.pdf",
        )

    except ValueError as e:
        return {"error": str(e)}, 400
    except Exception as e:
        app.logger.error(f"PDF generation failed: {e}")
        return {"error": "Failed to generate PDF"}, 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
