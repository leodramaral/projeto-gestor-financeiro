from django.urls import reverse

from goals.forms import GoalForm

AJAX = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}
SCRIPTS = ("dist/js/flatpickr.min.js", "dist/js/flatpickr-pt.js", "js/datepicker.js")


def test_deadline_widget_is_a_plain_date_input_marked_for_the_calendar(db):
    widget = GoalForm().fields["deadline"].widget
    assert widget.input_type == "date"
    assert "data-datepicker" in widget.attrs
    assert "pr-11" in widget.attrs["class"]


def test_other_fields_are_not_marked(db):
    fields = GoalForm().fields
    assert all("data-datepicker" not in fields[n].widget.attrs for n in ("name", "target_amount"))


def test_form_page_has_the_calendar_icon_and_the_scripts(logged):
    html = logged.get(reverse("goals:create")).content.decode()
    assert "data-datepicker" in html
    assert 'aria-hidden="true"' in html.split('name="deadline"')[1]  # the icon beside the field
    for script in SCRIPTS:
        assert script in html


def test_list_page_loads_the_scripts_for_the_modal(logged):
    html = logged.get(reverse("goals:list")).content.decode()
    for script in SCRIPTS:
        assert script in html


def test_modal_fragment_carries_no_scripts(logged):
    html = logged.get(reverse("goals:create"), **AJAX).content.decode()
    assert "data-datepicker" in html
    assert "flatpickr" not in html


def test_date_field_keeps_error_and_help_text(logged):
    response = logged.post(
        reverse("goals:create"),
        {"name": "x", "target_amount": "10,00", "saved_amount": "0,00", "deadline": "2020-01-01"},
    )
    html = response.content.decode()
    assert "O prazo não pode estar no passado." in html
    assert "Opcional." in html


def test_edit_keeps_the_saved_deadline_in_the_field(logged, user, make_goal, future):
    goal = make_goal(user, deadline=future)
    html = logged.get(reverse("goals:update", args=[goal.pk])).content.decode()
    assert f'value="{future.isoformat()}"' in html
