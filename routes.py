from flask import Blueprint, render_template, request, redirect
from models import db, RawMaterial, Production, Staff
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from flask import current_app
import csv
from io import StringIO
from flask import Response
from flask_mail import Message

print(f"Using email: {os.environ.get('MAIL_USERNAME')}")
print(f"Password length: {len(os.environ.get('MAIL_PASSWORD', ''))}")
def check_low_stock_and_notify():
    from flask_mail import Mail
    low_stock = [m for m in RawMaterial.query.all() if m.status in ['low_stock', 'out_of_stock']]
    
    if low_stock:
        material_list = "\n".join([
            f"- {m.name}: {m.quantity} {m.unit} remaining (minimum: {m.minimum_stock} {m.unit})"
            for m in low_stock
        ])
        
        msg = Message(
            subject="⚠️ PeellOps Low Stock Alert",
            recipients=[os.environ.get('MAIL_USERNAME')],
            body=f"""
Hello,

The following raw materials are running low at Peellnova Limited:

{material_list}

Please restock as soon as possible to avoid production delays.

— PeellOps System
            """
        )
        
        try:
            mail = Mail(current_app._get_current_object())
            mail.send(msg)
            print("✅ Email sent successfully")
        except Exception as e:
            print(f"❌ Email error: {e}")

main = Blueprint("main", __name__)

@main.route("/")
def dashboard():

    materials = RawMaterial.query.all()
    total_materials = len(materials)
    total_quantity = sum(m.quantity for m in materials)
    low_stock_materials = [m for m in materials if m.status in ["low_stock", "out_of_stock"]]

    batches = Production.query.all()
    total_batches = len(batches)
    batches_in_progress = len([b for b in batches if b.status == "in_progress"])
    batches_completed = len([b for b in batches if b.status == "completed"])
    total_peels_transformed = sum(b.peels_used for b in batches if b.status == "completed")
    recent_batches = Production.query.order_by(Production.date_created.desc()).limit(5).all()

    return render_template(
        "dashboard.html",
        total_materials=total_materials,
        total_quantity=total_quantity,
        low_stock_materials=low_stock_materials,
        total_batches=total_batches,
        batches_in_progress=batches_in_progress,
        batches_completed=batches_completed,
        total_peels_transformed=total_peels_transformed,
        recent_batches=recent_batches
    )


@main.route("/materials")
def materials():

    materials = RawMaterial.query.all()

    return render_template("materials.html", materials=materials)


@main.route("/add-material", methods=["GET", "POST"])
def add_material():

    if request.method == "POST":

        name = request.form["name"]
        quantity = float(request.form["quantity"])
        unit = request.form["unit"]
        material_type = request.form["material_type"]
        minimum_stock = float(request.form["minimum_stock"])
        supplier = request.form["supplier"]

        new_material = RawMaterial(
            name=name,
            quantity=quantity,
            unit=unit,
            material_type=material_type,
            minimum_stock=minimum_stock,
            supplier=supplier
        )

        db.session.add(new_material)
        db.session.commit()

        return redirect("/materials")

    return render_template("add_material.html")


@main.route("/edit-material/<int:id>", methods=["GET", "POST"])
def edit_material(id):

    material = RawMaterial.query.get_or_404(id)

    if request.method == "POST":

        material.name = request.form["name"]
        material.quantity = float(request.form["quantity"])
        material.unit = request.form["unit"]
        material.material_type = request.form["material_type"]
        material.minimum_stock = float(request.form["minimum_stock"])
        material.supplier = request.form["supplier"]

        db.session.commit()

        check_low_stock_and_notify()
        return redirect("/materials")

    return render_template("edit_material.html", material=material)

@main.route("/delete-material/<int:id>")
def delete_material(id):

    material = RawMaterial.query.get_or_404(id)

    db.session.delete(material)
    db.session.commit()

    return redirect("/materials")

@main.route("/add-batch", methods=["GET", "POST"])
def add_batch():

    if request.method == "POST":

        product_name = request.form["product_name"]
        product_type = request.form["product_type"]
        peels_used = float(request.form["peels_used"])
        quantity_produced = int(request.form["quantity_produced"])
        start_date = datetime.strptime(request.form["start_date"], "%Y-%m-%d").date()
        end_date = datetime.strptime(request.form["end_date"], "%Y-%m-%d").date()
        status = request.form["status"]
        supervisor = request.form["supervisor"]
        notes = request.form["notes"]
        progress = int(request.form["progress"])
        material_id = request.form["material_id"]

        # Deduct peels from raw material stock
        if material_id:
            material = RawMaterial.query.get(material_id)
            if material:
                if material.quantity < peels_used:
                    return render_template(
                        "add_batch.html",
                        materials=RawMaterial.query.all(),
                        error=f"Not enough stock. Only {material.quantity} {material.unit} of {material.name} available."
                    )
                material.quantity -= peels_used

        # Auto-generate batch number
        batch_count = Production.query.count()
        batch_number = f"BATCH-{datetime.now().year}-{str(batch_count + 1).zfill(4)}"

        new_batch = Production(
            batch_number=batch_number,
            product_name=product_name,
            product_type=product_type,
            peels_used=peels_used,
            quantity_produced=quantity_produced,
            start_date=start_date,
            end_date=end_date,
            status=status,
            progress=progress,
            supervisor=supervisor,
            notes=notes
        )

        db.session.add(new_batch)
        db.session.commit()

        check_low_stock_and_notify()
        return redirect("/batches")

    materials = RawMaterial.query.all()
    return render_template("add_batch.html", materials=materials)

@main.route("/batches")
def batches():
    batches = Production.query.order_by(Production.date_created.desc()).all()
    return render_template("batches.html", batches=batches)


@main.route("/edit-batch/<int:id>", methods=["GET", "POST"])
def edit_batch(id):

    batch = Production.query.get_or_404(id)

    if request.method == "POST":

        batch.product_name = request.form["product_name"]
        batch.product_type = request.form["product_type"]
        batch.peels_used = float(request.form["peels_used"])
        batch.quantity_produced = int(request.form["quantity_produced"])
        batch.start_date = datetime.strptime(request.form["start_date"], "%Y-%m-%d").date()
        batch.end_date = datetime.strptime(request.form["end_date"], "%Y-%m-%d").date()
        batch.status = request.form["status"]
        batch.supervisor = request.form["supervisor"]
        batch.notes = request.form["notes"]
        batch.progress = int(request.form["progress"])

        db.session.commit()

        return redirect("/batches")

    return render_template("edit_batch.html", batch=batch)


@main.route("/delete-batch/<int:id>")
def delete_batch(id):

    batch = Production.query.get_or_404(id)

    db.session.delete(batch)
    db.session.commit()

    return redirect("/batches")


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route("/staff")
def staff():
    staff_list = Staff.query.filter_by(is_active=True).order_by(Staff.first_name).all()
    return render_template("staff.html", staff_list=staff_list)

@main.route("/add-staff", methods=["GET", "POST"])
def add_staff():
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        role = request.form["role"]
        phone = request.form["phone"]
        email = request.form["email"]
        date_joined = datetime.strptime(request.form["date_joined"], "%Y-%m-%d").date()

        # Handle profile picture upload
        profile_pic = "default.png"
        if "profile_pic" in request.files:
            file = request.files["profile_pic"]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
                profile_pic = filename

        new_staff = Staff(
            first_name=first_name,
            last_name=last_name,
            role=role,
            phone=phone,
            email=email,
            date_joined=date_joined,
            profile_pic=profile_pic
        )

        db.session.add(new_staff)
        db.session.commit()

        return redirect("/staff")

    return render_template("add_staff.html")

@main.route("/edit-staff/<int:id>", methods=["GET", "POST"])
def edit_staff(id):
    staff = Staff.query.get_or_404(id)

    if request.method == "POST":
        staff.first_name = request.form["first_name"]
        staff.last_name = request.form["last_name"]
        staff.role = request.form["role"]
        staff.phone = request.form["phone"]
        staff.email = request.form["email"]
        staff.date_joined = datetime.strptime(request.form["date_joined"], "%Y-%m-%d").date()

        # Only update picture if a new one was uploaded
        if "profile_pic" in request.files:
            file = request.files["profile_pic"]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
                staff.profile_pic = filename

        db.session.commit()
        return redirect("/staff")

    return render_template("edit_staff.html", staff=staff)

@main.route("/deactivate-staff/<int:id>")
def deactivate_staff(id):
    staff = Staff.query.get_or_404(id)
    staff.is_active = False
    db.session.commit()
    return redirect("/staff")


@main.route("/reports")
def reports():
    materials = RawMaterial.query.all()
    batches = Production.query.all()
    staff_list = Staff.query.filter_by(is_active=True).all()

    # Summary stats
    total_peels_used = sum(b.peels_used for b in batches)
    total_units_produced = sum(b.quantity_produced for b in batches)
    batches_by_type = {}
    for b in batches:
        batches_by_type[b.product_type] = batches_by_type.get(b.product_type, 0) + b.quantity_produced

    return render_template(
        "reports.html",
        materials=materials,
        batches=batches,
        staff_list=staff_list,
        total_peels_used=total_peels_used,
        total_units_produced=total_units_produced,
        batches_by_type=batches_by_type
    )

@main.route("/export/materials")
def export_materials():
    materials = RawMaterial.query.all()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Name", "Type", "Quantity", "Unit", "Minimum Stock", "Supplier", "Status", "Date Added"])
    for m in materials:
        writer.writerow([m.id, m.name, m.material_type, m.quantity, m.unit, m.minimum_stock, m.supplier or "N/A", m.status, m.date_added.strftime('%d %b %Y')])
    output.seek(0)
    return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=materials.csv"})

@main.route("/export/batches")
def export_batches():
    batches = Production.query.all()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Batch Number", "Product Name", "Type", "Peels Used (kg)", "Qty Produced", "Progress", "Status", "Supervisor", "Start Date", "End Date"])
    for b in batches:
        writer.writerow([b.batch_number, b.product_name, b.product_type, b.peels_used, b.quantity_produced, f"{b.progress}%", b.status, b.supervisor or "N/A", b.start_date.strftime('%d %b %Y'), b.end_date.strftime('%d %b %Y')])
    output.seek(0)
    return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=batches.csv"})

