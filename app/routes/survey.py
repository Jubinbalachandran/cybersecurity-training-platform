@bp.route('/survey/<int:survey_id>/results/')
@login_required
def survey_results(survey_id):
    survey = SecuritySurvey.query.get_or_404(survey_id)
    questions = SurveyQuestion.query.filter_by(survey_id=survey_id).all()
    responses = SurveyResponse.query.filter_by(survey_id=survey_id).all()
    # Aggregate counts for each answer
    analytics = {q.id: {} for q in questions}
    for r in responses:
        ans = json.loads(r.answers)
        for q in questions:
            val = ans.get(f'q{q.id}')
            if val not in analytics[q.id]:
                analytics[q.id][val] = 0
            analytics[q.id][val] += 1
    return render_template('survey/results.html', survey=survey, questions=questions, analytics=analytics, responses=responses)