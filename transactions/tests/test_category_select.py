import re

import pytest
from django.template import Context, Template
from django.urls import reverse

from transactions.models import Category

pytestmark = pytest.mark.django_db


def render(categories, selected="", **overrides):
    source = (
        '{% load category_tags %}{% category_select name="category" field_id="id_category" '
        'categories=cats selected=sel placeholder="Selecione…" label="Categoria" %}'
    )
    return Template(source).render(Context({"cats": categories, "sel": selected, **overrides}))


@pytest.fixture
def pets(user, make_category):
    return make_category(user, "Pets", "paw-print", "amber")


def test_a_native_select_underneath_posts_the_same_value_without_javascript(pets):
    html = render(Category.objects.for_user(pets.user))

    assert '<select name="category" id="id_category"' in html
    assert '<option value="">Selecione…</option>' in html
    assert f'<option value="{pets.pk}">Pets</option>' in html


def test_every_category_gets_an_option_with_badge_and_name(pets):
    html = render(Category.objects.for_user(pets.user))

    options = re.findall(r'<li role="option"[^>]*>', html)
    assert len(options) == 1 + Category.objects.for_user(pets.user).count()
    assert 'data-value=""' in options[0]
    assert html.count("cat-badge") == len(options) - 1
    assert "cat-amber" in html and "<svg" in html


def test_the_chosen_category_is_marked_selected_in_the_native_select(pets):
    html = render(Category.objects.for_user(pets.user), selected=pets.pk)

    assert f'<option value="{pets.pk}" selected>Pets</option>' in html
    assert html.count(" selected>") == 1


def test_nothing_selected_marks_no_option(pets):
    assert " selected>" not in render(Category.objects.for_user(pets.user), selected="")


def test_listbox_roles_and_labels_for_assistive_technology(pets):
    html = render(Category.objects.for_user(pets.user))

    assert 'role="listbox"' in html and 'id="id_category-list"' in html
    assert 'role="combobox"' in html and 'aria-controls="id_category-list"' in html
    assert 'aria-haspopup="listbox"' in html
    assert 'aria-label="Categoria"' in html
    assert 'x-data="categorySelect"' in html


def test_custom_ui_is_hidden_until_javascript_enhances_it(pets):
    html = render(Category.objects.for_user(pets.user))

    assert 'style="display: none" x-show="enhanced"' in html


def test_category_names_are_escaped(user, make_category):
    evil = make_category(user, '<img src=x onerror="alert(1)">')

    html = render(Category.objects.for_user(user))

    assert "<img src=x" not in html
    assert "&lt;img src=x" in html
    assert str(evil.pk) in html


def test_only_the_categories_given_to_the_tag_are_listed(user, other_user, make_category):
    make_category(other_user, "Hobby")

    assert "Hobby" not in render(Category.objects.for_user(user))


def test_form_page_uses_the_floating_select_and_loads_its_script_before_alpine(logged_client, pets):
    content = logged_client.get(reverse("transactions:create")).content.decode()

    assert 'x-data="categorySelect"' in content
    assert content.index("js/category-select.js") < content.index("alpine.min.js")
    assert 'name="category"' in content and 'for="id_category-button"' in content


def test_edit_form_opens_with_the_current_category_selected(
    logged_client, user, make_transaction, pets
):
    item = make_transaction(user, category=pets)

    content = logged_client.get(reverse("transactions:update", args=[item.pk])).content.decode()

    assert f'<option value="{pets.pk}" selected>Pets</option>' in content


def test_a_rejected_category_keeps_the_error_next_to_the_select(logged_client):
    data = {"kind": "expense", "amount": "5", "date": "2026-10-02", "description": "x"}

    content = logged_client.post(reverse("transactions:create"), data).content.decode()

    assert "Escolha a categoria da despesa." in content
    assert 'x-data="categorySelect"' in content


def test_filter_uses_the_floating_select_with_all_categories_as_placeholder(
    logged_client, user, make_transaction, pets
):
    make_transaction(user)

    content = logged_client.get(reverse("transactions:list")).content.decode()

    assert 'id="category-filter"' in content
    assert "Todas as categorias" in content
    assert f'<option value="{pets.pk}">Pets</option>' in content
