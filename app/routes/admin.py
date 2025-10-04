@bp.route('/report')
@login_required
def report():
    if current_user.role not in ['admin', 'superadmin']:
        return "Access denied", 403
    user_id = request.args.get('user_id', type=int)
    module_id = request.args.get('module_id', type=int)

    users = User.query.all()
    modules = TrainingModule.query.all()
    progress = UserProgress.query.all()
    progress_dict = {(p.user_id, p.module_id): p.completed for p in progress}

    filtered_users = [u for u in users if (not user_id) or (u.id == user_id)]
    filtered_modules = [m for m in modules if (not module_id) or (m.id == module_id)]

    # Calculate completion percentages
    user_completion = {}
    for user in filtered_users:
        total = len(filtered_modules)
        completed = sum(1 for m in filtered_modules if progress_dict.get((user.id, m.id), False))
        percent = (completed / total * 100) if total else 0
        user_completion[user.id] = percent

    module_completion = {}
    for module in filtered_modules:
        total = len(filtered_users)
        completed = sum(1 for u in filtered_users if progress_dict.get((u.id, module.id), False))
        percent = (completed / total * 100) if total else 0
        module_completion[module.id] = percent

    # After computing user_completion and module_completion
	user_labels = [user.username for user in filtered_users]
	user_data = [user_completion[user.id] for user in filtered_users]
	module_labels = [module.title for module in filtered_modules]
	module_data = [module_completion[module.id] for module in filtered_modules]

    return render_template(
       'admin/report.html',
       # ...other context...
       user_labels=user_labels,
       user_data=user_data,
       module_labels=module_labels,
       module_data=module_data
)
   