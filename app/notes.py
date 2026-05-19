from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
# pyrefly: ignore [missing-import]
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Note

notes = Blueprint("notes", __name__)

@notes.route("/dashboard")
@login_required
def dashboard():
    user_notes = Note.query.filter_by(user_id=current_user.id).order_by(Note.date_created.desc()).all()
    return render_template("dashboard.html", notes=user_notes)

@notes.route("/note/new", methods=["GET", "POST"])
@login_required
def create_note():
    if request.method == "POST":
        if request.is_json:
            data = request.get_json() or {}
            title = data.get("title", "").strip()
            content = data.get("content", "").strip()
        else:
            title = request.form.get("title", "").strip()
            content = request.form.get("content", "").strip()
        
        if not title or not content:
            if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return {"error": "Title and Content are required."}, 400
            flash("Title and Content are required.", "danger")
            return redirect(url_for("notes.create_note"))
            
        if len(title) > 200 or len(content) > 10000:
            if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return {"error": "Oversized input limit exceeded."}, 400
            flash("Oversized input. Title must be under 200 characters and content under 10000 characters.", "danger")
            return redirect(url_for("notes.create_note"))
            
        new_note = Note(title=title, content=content, user_id=current_user.id)
        db.session.add(new_note)
        db.session.commit()
        
        if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return {
                "success": True,
                "message": "Note created successfully!",
                "note": {
                    "id": new_note.id,
                    "title": new_note.title,
                    "content": new_note.content,
                    "date_created": new_note.date_created.strftime('%b %d, %Y')
                }
            }
            
        flash("Note created successfully!", "success")
        return redirect(url_for("notes.dashboard"))
        
    return render_template("note_form.html", action="Create", note=None)

@notes.route("/note/<int:note_id>/edit", methods=["GET", "POST"])
@login_required
def edit_note(note_id):
    note = db.get_or_404(Note, note_id)
    
    # Secure validation: User must be owner
    if note.user_id != current_user.id:
        if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return {"error": "Unauthorized"}, 403
        abort(403)
        
    if request.method == "POST":
        if request.is_json:
            data = request.get_json() or {}
            title = data.get("title", "").strip()
            content = data.get("content", "").strip()
        else:
            title = request.form.get("title", "").strip()
            content = request.form.get("content", "").strip()
        
        if not title or not content:
            if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return {"error": "Title and Content are required."}, 400
            flash("Title and Content are required.", "danger")
            return redirect(url_for("notes.edit_note", note_id=note.id))
            
        if len(title) > 200 or len(content) > 10000:
            if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return {"error": "Oversized input limit exceeded."}, 400
            flash("Oversized input. Title must be under 200 characters and content under 10000 characters.", "danger")
            return redirect(url_for("notes.edit_note", note_id=note.id))
            
        note.title = title
        note.content = content
        db.session.commit()
        
        if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return {
                "success": True,
                "message": "Note updated successfully!",
                "note": {
                    "id": note.id,
                    "title": note.title,
                    "content": note.content,
                    "date_created": note.date_created.strftime('%b %d, %Y')
                }
            }
            
        flash("Note updated successfully!", "success")
        return redirect(url_for("notes.dashboard"))
        
    return render_template("note_form.html", action="Edit", note=note)

@notes.route("/note/<int:note_id>/delete", methods=["POST"])
@login_required
def delete_note(note_id):
    note = db.get_or_404(Note, note_id)
    
    # Secure validation: User must be owner
    if note.user_id != current_user.id:
        if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return {"error": "Unauthorized"}, 403
        abort(403)
        
    db.session.delete(note)
    db.session.commit()
    
    if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return {"success": True, "message": "Note deleted successfully!"}
        
    flash("Note deleted successfully!", "success")
    return redirect(url_for("notes.dashboard"))
