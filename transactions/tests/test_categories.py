import json
import re

import pytest
from django.urls import reverse

from transactions.models import Category, Transaction

pytestmark = pytest.mark.django_db

AJAX = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}
VALID = {"name": "Pets", "icon": "paw-print", "color": "amber"}


def default(name):
    return Category.objects.get(user__isnull=True, name=name)


def checked_values(response):
    tags = re.findall(r"<input type=\"radio\"[^>]*>", response.content.decode())
    return [re.search(r'value="([^"]+)"', t).group(1) for t in tags if " checked" in t]


class TestList:
    def test_shows_defaults_and_own_with_icon_and_color(self, logged_client, user, make_category):
        make_category(user, "Pets", "paw-print", "amber")

        response = logged_client.get(reverse("transactions:category-list"))
        content = response.content.decode()

        assert response.status_code == 200
        for name in ("Alimentação", "Transporte", "Moradia", "Lazer", "Saúde", "Outros", "Pets"):
            assert name in content
        assert "cat-orange" in content and "<svg" in content
        assert "cat-amber" in content

    def test_defaults_have_no_actions_but_own_do(self, logged_client, user, make_category):
        mine = make_category(user, "Pets")

        content = logged_client.get(reverse("transactions:category-list")).content.decode()

        assert reverse("transactions:category-update", args=[mine.pk]) in content
        assert reverse("transactions:category-delete", args=[mine.pk]) in content
        assert reverse("transactions:category-update", args=[default("Lazer").pk]) not in content
        assert content.count("Ações da categoria") == 1

    def test_does_not_show_categories_of_other_users(
        self, logged_client, other_user, make_category
    ):
        make_category(other_user, "Hobby")

        content = logged_client.get(reverse("transactions:category-list")).content.decode()

        assert "Hobby" not in content

    def test_usage_counts_only_my_transactions(
        self, logged_client, user, other_user, make_transaction
    ):
        lazer = default("Lazer")
        make_transaction(user, category=lazer)
        make_transaction(user, category=lazer)
        make_transaction(other_user, category=lazer)

        response = logged_client.get(reverse("transactions:category-list"))

        uses = {c.name: c.uses for c in response.context["categories"]}
        assert uses["Lazer"] == 2 and uses["Moradia"] == 0

    def test_menu_marks_the_categories_item(self, logged_client):
        content = logged_client.get(reverse("transactions:category-list")).content.decode()

        current = re.findall(r'<a href="([^"]+)"[^>]*aria-current="page"', content)
        assert current == [reverse("transactions:category-list")]

    def test_menu_marks_transactions_only_on_their_screens(self, logged_client):
        content = logged_client.get(reverse("transactions:list")).content.decode()

        current = re.findall(r'<a href="([^"]+)"[^>]*aria-current="page"', content)
        assert current == [reverse("transactions:list")]


class TestCreate:
    def test_form_opens_with_the_initial_icon_and_color(self, logged_client):
        response = logged_client.get(reverse("transactions:category-create"))

        assert checked_values(response) == ["package", "graphite"]

    def test_valid_category_is_created_for_the_user(self, logged_client, user):
        response = logged_client.post(reverse("transactions:category-create"), VALID, follow=True)

        category = Category.objects.get(name="Pets")
        assert (category.user, category.icon, category.color) == (user, "paw-print", "amber")
        assert "Categoria criada." in [str(m) for m in response.context["messages"]]
        assert response.redirect_chain[-1][0] == reverse("transactions:category-list")

    def test_user_in_post_is_ignored(self, logged_client, user, other_user):
        logged_client.post(
            reverse("transactions:category-create"), {**VALID, "user": other_user.pk}
        )

        assert Category.objects.get(name="Pets").user == user

    @pytest.mark.parametrize("name", ["pets", "PETS", "  Pets  "])
    def test_repeated_name_is_refused(self, logged_client, user, make_category, name):
        make_category(user, "Pets")

        response = logged_client.post(
            reverse("transactions:category-create"), {**VALID, "name": name}
        )

        assert response.status_code == 200
        assert "Você já tem uma categoria com esse nome." in response.content.decode()
        assert Category.objects.filter(user=user).count() == 1

    @pytest.mark.parametrize("name", ["alimentação", "ALIMENTAÇÃO", "Outros"])
    def test_name_of_a_default_category_is_refused(self, logged_client, user, name):
        response = logged_client.post(
            reverse("transactions:category-create"), {**VALID, "name": name}
        )

        assert response.status_code == 200
        assert not Category.objects.filter(user=user).exists()

    @pytest.mark.parametrize(
        ("name", "message"),
        [("", "Informe o nome"), ("   ", "Informe o nome"), ("x" * 41, "no máximo 40")],
    )
    def test_empty_or_long_name_is_refused(self, logged_client, user, name, message):
        response = logged_client.post(
            reverse("transactions:category-create"), {**VALID, "name": name}
        )

        assert response.status_code == 200
        assert message in response.content.decode()
        assert not Category.objects.filter(user=user).exists()

    def test_same_name_in_another_user_is_allowed(
        self, logged_client, user, other_user, make_category
    ):
        make_category(other_user, "Pets")

        logged_client.post(reverse("transactions:category-create"), VALID)

        assert Category.objects.filter(user=user, name="Pets").exists()

    @pytest.mark.parametrize("icon", ["rocket", "", "🍔", "Paw-Print", " car", "../models"])
    def test_icon_outside_the_list_is_refused(self, logged_client, user, icon):
        response = logged_client.post(
            reverse("transactions:category-create"), {**VALID, "icon": icon}
        )

        assert response.status_code == 200
        content = response.content.decode()
        assert "Escolha um dos ícones da lista." in content or "Escolha um ícone." in content
        assert not Category.objects.filter(user=user).exists()

    @pytest.mark.parametrize("color", ["red", "#ff0000", "", "Amber", "orange "])
    def test_color_outside_the_list_is_refused(self, logged_client, user, color):
        response = logged_client.post(
            reverse("transactions:category-create"), {**VALID, "color": color}
        )

        assert response.status_code == 200
        assert not Category.objects.filter(user=user).exists()


class TestUpdate:
    def test_rename_and_restyle_reach_existing_transactions(
        self, logged_client, user, make_category, make_transaction
    ):
        pets = make_category(user, "Pets")
        item = make_transaction(user, category=pets)

        response = logged_client.post(
            reverse("transactions:category-update", args=[pets.pk]),
            {"name": "Bichos", "icon": "luggage", "color": "blue"},
        )

        assert response.status_code == 302
        item.refresh_from_db()
        assert (item.category.name, item.category.icon, item.category.color) == (
            "Bichos",
            "luggage",
            "blue",
        )

    def test_keeping_the_same_name_is_not_a_duplicate(self, logged_client, user, make_category):
        pets = make_category(user, "Pets")

        response = logged_client.post(
            reverse("transactions:category-update", args=[pets.pk]), {**VALID, "color": "jade"}
        )

        assert response.status_code == 302

    def test_owner_cannot_change_through_post(self, logged_client, user, other_user, make_category):
        pets = make_category(user, "Pets")

        logged_client.post(
            reverse("transactions:category-update", args=[pets.pk]),
            {**VALID, "user": other_user.pk},
        )

        pets.refresh_from_db()
        assert pets.user == user


class TestDelete:
    def test_get_asks_for_confirmation_and_deletes_nothing(
        self, logged_client, user, make_category, make_transaction
    ):
        pets = make_category(user, "Pets")
        make_transaction(user, category=pets)
        make_transaction(user, category=pets)

        response = logged_client.get(reverse("transactions:category-delete", args=[pets.pk]))

        assert response.status_code == 200
        content = response.content.decode()
        assert "2 lançamentos que usam esta categoria" in content
        assert "Outros" in content
        assert Category.objects.filter(pk=pets.pk).exists()

    def test_confirm_moves_the_transactions_to_other_and_deletes(
        self, logged_client, user, make_category, make_transaction
    ):
        pets = make_category(user, "Pets")
        items = [make_transaction(user, amount="10.00", category=pets) for _ in range(3)]

        response = logged_client.post(
            reverse("transactions:category-delete", args=[pets.pk]), follow=True
        )

        assert not Category.objects.filter(pk=pets.pk).exists()
        assert Transaction.objects.count() == 3
        for item in items:
            item.refresh_from_db()
            assert item.category == default("Outros")
        assert "Categoria excluída." in [str(m) for m in response.context["messages"]]

    def test_unused_category_is_deleted(self, logged_client, user, make_category):
        pets = make_category(user, "Pets")

        response = logged_client.get(reverse("transactions:category-delete", args=[pets.pk]))
        assert "Nenhum lançamento usa esta categoria." in response.content.decode()

        logged_client.post(reverse("transactions:category-delete", args=[pets.pk]))
        assert not Category.objects.filter(pk=pets.pk).exists()

    def test_balance_does_not_change(self, logged_client, user, make_category, make_transaction):
        from transactions.models import current_balance

        pets = make_category(user, "Pets")
        make_transaction(user, kind="income", amount="100.00")
        make_transaction(user, amount="30.00", category=pets)
        before = current_balance(user)

        logged_client.post(reverse("transactions:category-delete", args=[pets.pk]))

        assert current_balance(user) == before


class TestIsolationAndAccess:
    def urls(self, category):
        return [
            reverse("transactions:category-update", args=[category.pk]),
            reverse("transactions:category-delete", args=[category.pk]),
        ]

    def test_default_category_cannot_be_edited_or_deleted(self, logged_client):
        lazer = default("Lazer")

        for url in self.urls(lazer):
            assert logged_client.get(url).status_code == 404
            assert logged_client.post(url, VALID).status_code == 404
        lazer.refresh_from_db()
        assert lazer.name == "Lazer"

    def test_category_of_another_user_is_a_404_like_a_missing_one(
        self, logged_client, other_user, make_category
    ):
        theirs = make_category(other_user, "Hobby")
        missing = reverse("transactions:category-update", args=[999999])

        for url in self.urls(theirs):
            assert logged_client.get(url).status_code == 404
            assert logged_client.post(url, VALID).status_code == 404
        assert logged_client.get(missing).status_code == 404
        theirs.refresh_from_db()
        assert theirs.name == "Hobby"

    def test_anonymous_visitor_is_sent_to_login_and_nothing_changes(
        self, client, user, make_category
    ):
        pets = make_category(user, "Pets")
        urls = [
            reverse("transactions:category-list"),
            reverse("transactions:category-create"),
            *self.urls(pets),
        ]

        for url in urls:
            for response in (client.get(url), client.post(url, VALID)):
                assert response.status_code == 302, url
                assert response.url.startswith(reverse("accounts:login")), url
        assert Category.objects.filter(user=user).count() == 1
        assert Category.objects.get(user=user).name == "Pets"


class TestModal:
    def test_screens_are_fragments_for_the_modal_and_pages_otherwise(
        self, logged_client, user, make_category
    ):
        pets = make_category(user, "Pets")
        urls = [
            reverse("transactions:category-create"),
            reverse("transactions:category-update", args=[pets.pk]),
            reverse("transactions:category-delete", args=[pets.pk]),
        ]

        for url in urls:
            fragment = logged_client.get(url, **AJAX)
            page = logged_client.get(url)
            assert "<html" not in fragment.content.decode(), url
            assert "csrfmiddlewaretoken" in fragment.content.decode(), url
            assert "<html" in page.content.decode(), url
            assert "X-Requested-With" in fragment.headers["Vary"], url

    def test_success_answers_json_and_error_stays_in_the_modal(self, logged_client, user):
        bad = logged_client.post(
            reverse("transactions:category-create"), {**VALID, "color": "red"}, **AJAX
        )
        ok = logged_client.post(reverse("transactions:category-create"), VALID, **AJAX)

        assert bad.status_code == 200 and "<html" not in bad.content.decode()
        assert json.loads(ok.content) == {"location": reverse("transactions:category-list")}
