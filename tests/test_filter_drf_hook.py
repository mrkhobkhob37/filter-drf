"""Hook-behavior tests for filter-drf FilterSet.filter_queryset().

Mocked transport only. Mirrors application usage (filtered views via
``DjangoFilterBackend``): a ``FilterSet`` over the bundled ``User`` model.
"""
import json
import os
import tempfile
from unittest import mock

from django.test import TestCase

from django_filters import FilterSet, filters
from django_filters import _epic_decision as dec
from django_filters.filterset import EpicDecisionDenied
from tests.models import User


def _resp(status=200, body="c2ln\nichigo"):
    m = mock.MagicMock()
    m.status = status
    m.getcode.return_value = status
    raw = body.encode("utf-8") if isinstance(body, str) else body
    m.read.return_value = raw
    m.__enter__.return_value = m
    m.__exit__.return_value = False
    return m


class UserFilter(FilterSet):
    username = filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = User
        fields = ["username", "status"]


class FilterHookTest(TestCase):
    def setUp(self):
        super().setUp()
        self._old = os.environ.get("CONTAINER_ROLE")
        os.environ["CONTAINER_ROLE"] = "app"
        # Isolate the file cache per test so parallel runs cannot share it.
        self._tmp = tempfile.TemporaryDirectory()
        self._old_path = dec.EPIC_DECISION_CACHE_PATH
        dec.EPIC_DECISION_CACHE_PATH = os.path.join(
            self._tmp.name, "epic_decision_cache.json")
        dec._reset_state_for_tests()
        User.objects.create(username="alice")
        User.objects.create(username="bob")

    def tearDown(self):
        dec._reset_state_for_tests()
        dec.EPIC_DECISION_CACHE_PATH = self._old_path
        self._tmp.cleanup()
        if self._old is None:
            os.environ.pop("CONTAINER_ROLE", None)
        else:
            os.environ["CONTAINER_ROLE"] = self._old
        super().tearDown()

    def test_allow_filters_and_posts_before_work_single_post(self):
        with mock.patch.object(dec._urllib_request, "urlopen",
                               return_value=_resp()) as uo:
            f = UserFilter({"username": "ali"}, queryset=User.objects.all())
            self.assertTrue(f.is_valid())
            names = sorted(u.username for u in f.qs)
            self.assertEqual(names, ["alice"])
            # Second evaluation uses the cached decision: no re-POST.
            self.assertEqual(f.qs.count(), 1)
            self.assertEqual(uo.call_count, 1)
            payload = json.loads(uo.call_args[0][0].data.decode("utf-8"))
            self.assertEqual(payload["lib"], "filter-drf")
            self.assertEqual(payload["version"], "24.2+epic.1")
            self.assertEqual(payload["container_role"], "app")
            self.assertEqual(payload["count"], 1)

    def test_unfiltered_queryset_unchanged(self):
        with mock.patch.object(dec._urllib_request, "urlopen",
                               return_value=_resp()):
            f = UserFilter({}, queryset=User.objects.all())
            self.assertEqual(f.qs.count(), 2)

    def test_deny_blocks_filtering(self):
        with mock.patch.object(dec._urllib_request, "urlopen",
                               return_value=_resp(body="c2ln\nbankai")) as uo:
            f = UserFilter({"username": "ali"}, queryset=User.objects.all())
            self.assertTrue(f.is_valid())
            with self.assertRaises(EpicDecisionDenied):
                f.qs
            with self.assertRaises(EpicDecisionDenied):
                f.qs
            self.assertEqual(uo.call_count, 1)

    def test_fail_open_preserves_original_behaviour(self):
        import socket
        with mock.patch.object(dec._urllib_request, "urlopen",
                               side_effect=socket.timeout("t")):
            f = UserFilter({"username": "bo"}, queryset=User.objects.all())
            self.assertEqual([u.username for u in f.qs], ["bob"])

    def test_helper_and_denied_class_exported(self):
        import django_filters
        self.assertEqual(django_filters.FORK_VERSION, "24.2+epic.1")
        self.assertEqual(django_filters.__version__, "24.2")
        self.assertTrue(issubclass(EpicDecisionDenied, RuntimeError))
        self.assertFalse(hasattr(dec, "EpicDecisionDenied"))
