from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect
from models import Contact, Phone, session
from sqlalchemy import func


app = Flask(__name__)
app.debug = True
app.env = "development"


def create_phones_list(contact):
    query = session.query(Phone).filter_by(contact_id=contact.id)
    if query.count() == 0:
        return ''
    else:
        return ', '.join([phone.phone_number for phone in query.all()])


@app.route("/", methods=["GET"], strict_slashes=False)
def index():
    sort_by = request.args.get("sorted", default="name")
    contacts_db = session.query(Contact).order_by(sort_by).all()
    contacts_view = []
    for contact in contacts_db:
        birthday = datetime.strftime(
            contact.birthday, '%d.%m.%Y') if contact.birthday else ''
        append_to_view = True
        if request.args.get("search"):
            search_str = request.args.get("search").lower()
            append_to_view = append_to_view and (search_str in str(contact.name).lower() or
                                                 search_str in str(contact.address).lower() or
                                                 search_str in create_phones_list(contact) or
                                                 search_str in str(contact.email).lower() or
                                                 search_str in birthday)
        if request.args.get("birthday_days"):
            if birthday:
                current_date = datetime.now().date()
                timedelta_filter = timedelta(
                    days=int(request.args.get("birthday_days")))
                birthday_date = contact.birthday
                current_birthday = birthday_date.replace(
                    year=current_date.year)
                append_to_view = append_to_view and (
                    current_date <= current_birthday <= current_date + timedelta_filter)
            else:
                append_to_view = False

        if append_to_view:
            contacts_view.append(
                {'id': contact.id,
                 'name': contact.name,
                 'address': contact.address,
                 'email': contact.email,
                 'phones': create_phones_list(contact),
                 'birthday': birthday})

    if request.args.get("added"):
        action_word = 'added'
        contact_name = request.args.get("added")
    if request.args.get("changed"):
        action_word = 'changed'
        contact_name = request.args.get("changed")
    if request.args.get("deleted"):
        action_word = 'deleted'
        contact_name = request.args.get("deleted")
    if request.args.get("dphones"):
        duplicated_phones = request.args.get("dphones")
    else:
        duplicated_phones = ''

    message = ''
    alert = ''
    if request.args.get("added") or request.args.get("changed") or request.args.get("deleted"):
        message = f'Contact <b>{contact_name}</b> has been successfully {action_word}.'
        if duplicated_phones:
            alert = f'Phone number <b>{duplicated_phones}</b> has not been added because there is such phone number in the database already!'

    return render_template("index.html", contacts=contacts_view, search_str=request.args.get("search"),
                           size=len(contacts_view), message=message, alert=alert, sort_by=sort_by,
                           birthday_days=request.args.get("birthday_days"))


def extend_arg_str(arg_str, request_args):
    if request_args.get('sorted'):
        arg_str += f"&sorted={request_args.get('sorted')}"
    if request_args.get('search'):
        arg_str += f"&search={request_args.get('search')}"
    if request_args.get('birthday_days'):
        arg_str += f"&birthday_days={request_args.get('birthday_days')}"
    print(f"Args = {request_args}")
    return arg_str


@app.route("/delete/<id>", strict_slashes=False)
def delete(id):
    contact_name = session.query(Contact).filter_by(id=id).first().name
    session.query(Phone).filter_by(contact_id=id).delete()
    session.commit()
    session.query(Contact).filter_by(id=id).delete()
    session.commit()
    return redirect(extend_arg_str(f"/?deleted={contact_name}", request.args))


def add_phone(request, id):
    duplicated_phones = []
    for i in range(3):
        phone_number = request.form.get(f"phone{i+1}")
        if phone_number:
            if session.query(Phone).filter_by(phone_number=phone_number).count() > 0:
                duplicated_phones.append(phone_number)
            else:
                phone = Phone(phone_number=phone_number, contact_id=id)
                session.add(phone)
                session.commit()
    return duplicated_phones


@ app.route("/contact/", methods=["GET", "POST"], strict_slashes=False)
def add_contact():
    if request.method == "POST":
        name = request.form.get("name")
        address = request.form.get("address")
        email = request.form.get("email")
        birthday = datetime.strptime(request.form.get(
            "birthday"), '%Y-%m-%d') if request.form.get("birthday") else None
        print("-" * 20, type(birthday), "-" * 20)
        contact = Contact(name=name, address=address,
                          email=email, birthday=birthday)
        session.add(contact)
        session.commit()
        contact_id = session.query(func.max(Contact.id)).first()[0]
        dublicated_phones = add_phone(request, contact_id)
        if dublicated_phones == []:
            arg_str = f"/?added={contact.name}"
        else:
            arg_str = f"/?added={contact.name}&dphones={', '.join(dublicated_phones)}"
        return redirect(extend_arg_str(arg_str, request.form))
    else:
        if session.query(Contact).count() == 0:
            contact_id = 1
        else:
            contact_id = session.query(func.max(Contact.id)).first()[0] + 1
        return render_template("contact.html", phones=[], id=contact_id, action="/contact")


@ app.route("/edit/<id>", methods=["GET", "POST"], strict_slashes=False)
def edit_contact(id):
    if request.method == "POST":
        name = request.form.get("name")
        address = request.form.get("address")
        email = request.form.get("email")
        birthday = datetime.strptime(request.form.get(
            "birthday"), '%Y-%m-%d') if request.form.get("birthday") else None
        session.query(Contact).filter_by(id=id).update(
            {'name': name, 'address': address, 'email': email, 'birthday': birthday})
        session.commit()
        session.query(Phone).filter_by(contact_id=id).delete()
        session.commit()
        dublicated_phones = add_phone(request, id)
        if dublicated_phones == []:
            arg_str = f"/?changed={name}"
        else:
            arg_str = f"/?changed={name}&dphones={', '.join(dublicated_phones)}"
        return redirect(extend_arg_str(arg_str, request.form))
    else:
        contact = session.query(Contact).filter_by(id=id).first()
        phones = [phone.phone_number for phone in session.query(
            Phone).filter_by(contact_id=id).all()]
        return render_template("contact.html", name=contact.name, address=contact.address,
                               email=contact.email, birthday=contact.birthday, phones=phones, id=id, action=f"/edit/{id}")


if __name__ == "__main__":
    app.run()
