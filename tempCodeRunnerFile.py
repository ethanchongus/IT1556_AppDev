 if add_form.validate_on_submit() and add_form.submit.data:
        try:
            name = add_form.event_name.data
            desc = add_form.event_desc.data
            print(name,desc)
            create_event(name, desc)
            flash(f"Tour '{name}' has been successfully added.", "success")
        except Exception as e:
            flash("Failed to add tour. Please try again.", "danger")
            print(e)
        return redirect(url_for('admin_events'))