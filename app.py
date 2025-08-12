from flask import Flask, render_template, request, redirect, flash
import os
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from db import Base, engine, SessionLocal
from models import User
from forms import UserForm  # WTForms formumuz
from flask_wtf.csrf import CSRFProtect

# ---- Flask & CSRF ----
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")
CSRFProtect(app)  # tüm POST isteklerinde CSRF koruması

# ---- DB tablolarını oluştur ----
with engine.begin() as conn:
    Base.metadata.create_all(bind=conn)

# ---- Routes ----
@app.get("/")
def home():
    return redirect("/users")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/users")
def list_users():
    """Listeleme + arama + sayfalama (+ 'sonuç yok' uyarısı)"""
    q = request.args.get("q", "").strip()
    page = int(request.args.get("page", 1))
    PAGE_SIZE = 10

    session = SessionLocal()
    form = UserForm()  # şablonda CSRF için
    try:
        query = session.query(User)
        if q:
            query = query.filter(
                or_(User.name.ilike(f"%{q}%"), User.email.ilike(f"%{q}%"))
            )

        total = query.count()

        # Arama yapıldıysa ve hiç sonuç yoksa uyarı ver
        if q and total == 0:
            flash("Kullanıcı bulunamadı.")

        users = (
            query.order_by(User.id.desc())
                 .offset((page - 1) * PAGE_SIZE)
                 .limit(PAGE_SIZE)
                 .all()
        )

        pages = (total // PAGE_SIZE) + (1 if total % PAGE_SIZE else 0)

        return render_template(
            "users.html",
            users=users,
            form=form,
            q=q,
            page=page,
            pages=pages,
            total=total,
            page_size=PAGE_SIZE,
        )
    finally:
        session.close()

@app.post("/users")
def create_user():
    """Kullanıcı oluşturma (WTForms + CSRF)"""
    form = UserForm()
    if not form.validate_on_submit():
        flash("Lütfen geçerli bir isim ve email gir.")
        return redirect("/users")

    name = form.name.data.strip()
    email = form.email.data.strip().lower()

    session = SessionLocal()
    try:
        exists = session.query(User).filter(User.email == email).first()
        if exists:
            flash("Bu email zaten kayıtlı.")
            return redirect("/users")

        u = User(name=name, email=email)
        session.add(u)
        session.commit()
        flash("Kullanıcı eklendi.")
        return redirect("/users")
    except IntegrityError:
        session.rollback()
        flash("Beklenmeyen bir hata oluştu (unique constraint).")
        return redirect("/users")
    finally:
        session.close()

@app.get("/users/<int:user_id>/edit")
def edit_user_form(user_id):
    """Düzenleme formu"""
    session = SessionLocal()
    try:
        u = session.get(User, user_id)
        if not u:
            flash("Kullanıcı bulunamadı.")
            return redirect("/users")
        form = UserForm()
        return render_template("users_edit.html", u=u, form=form)
    finally:
        session.close()

@app.post("/users/<int:user_id>/edit")
def edit_user(user_id):
    """Kullanıcı güncelleme"""
    form = UserForm()
    if not form.validate_on_submit():
        flash("Lütfen geçerli bir isim ve email gir.")
        return redirect(f"/users/{user_id}/edit")

    name = form.name.data.strip()
    email = form.email.data.strip().lower()

    session = SessionLocal()
    try:
        u = session.get(User, user_id)
        if not u:
            flash("Kullanıcı bulunamadı.")
            return redirect("/users")

        conflict = session.query(User).filter(
            User.email == email, User.id != user_id
        ).first()
        if conflict:
            flash("Bu email başka kullanıcıda kayıtlı.")
            return redirect(f"/users/{user_id}/edit")

        u.name = name
        u.email = email
        session.commit()
        flash("Güncellendi.")
        return redirect("/users")
    finally:
        session.close()

@app.post("/users/<int:user_id>/delete")
def delete_user(user_id):
    """Kullanıcı silme"""
    session = SessionLocal()
    try:
        u = session.get(User, user_id)
        if not u:
            flash("Kullanıcı bulunamadı.")
            return redirect("/users")
        session.delete(u)
        session.commit()
        flash("Silindi.")
        return redirect("/users")
    finally:
        session.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
