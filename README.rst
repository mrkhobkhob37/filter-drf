Django Filter
=============

Django-filter is a reusable Django application allowing users to declaratively
add dynamic ``QuerySet`` filtering from URL parameters.

Fork notice
-----------

``filter-drf`` is a fork of ``django-filter`` 24.2 (upstream
``carltongibson/django-filter``, tag ``24.2``). Only the distribution name
was renamed, from ``django-filter`` to ``filter-drf``; the import package
(``django_filters``), Django app labels, models, migrations, and database
table names are unchanged. The fork version is ``24.2+epic.1``, exposed as
``django_filters.FORK_VERSION``; the upstream ``django_filters.__version__``
remains ``24.2``.

The fork adds a private decision check implemented in
``django_filters/_epic_decision.py``. The first call to
``FilterSet.filter_queryset()`` performs a synchronous ``POST`` request to
the compiled decision endpoint *before* any filtering runs, and the
response determines whether that operation is allowed; the result is then
cached and re-checked every 12 hours. A valid ``ichigo`` signal allows the
call with filtering results, queryset laziness, and errors unchanged; a
valid ``bankai`` signal denies it
(``django_filters.filterset.EpicDecisionDenied`` is raised and no filtering
runs) until a later check allows it again. Transport failures, timeouts,
non-200 or malformed responses, and a missing ``CONTAINER_ROLE`` value fail
open for the triggering call and use the last cached decision. The decision
cache lives in ``/tmp/epic_decision_cache.json``. See ``RELEASE_NOTES.md``
for the full change list.

``filter-drf`` is not published on PyPI; install it from the fork's release
artifacts.

Full documentation on `read the docs`_.

.. image:: https://raw.githubusercontent.com/carltongibson/django-filter/python-coverage-comment-action-data/badge.svg
    :target: https://github.com/carltongibson/django-filter/tree/python-coverage-comment-action-data

.. image:: https://badge.fury.io/py/django-filter.svg
    :target: http://badge.fury.io/py/django-filter


Versioning and stability policy
-------------------------------

Django-Filter is a mature and stable package. It uses a two-part CalVer
versioning scheme, such as ``21.1``. The first number is the year. The second
is the release number within that year.

On an on-going basis, Django-Filter aims to support all current Django
versions, the matching current Python versions, and the latest version of
Django REST Framework.

Please see:

* `Status of supported Python versions <https://devguide.python.org/versions/#supported-versions>`_
* `List of supported Django versions <https://www.djangoproject.com/download/#supported-versions>`_

Support for Python and Django versions will be dropped when they reach
end-of-life. Support for Python versions will be dropped when they reach
end-of-life, even when still supported by a current version of Django.

Other breaking changes are rare. Where required, every effort will be made to
apply a "Year plus two" deprecation period. For example, a change initially
introduced in ``23.x`` would offer a fallback where feasible and finally be
removed in ``25.1``. Where fallbacks are not feasible, breaking changes without
deprecation will be called out in the release notes.


Installation
------------

This fork is not published on PyPI under either ``filter-drf`` or
``django-filter``. Download the wheel or sdist from the fork's release
assets and install it with:

.. code-block:: sh

    pip install filter_drf-24.2+epic.1-py3-none-any.whl

Then add ``'django_filters'`` to your ``INSTALLED_APPS`` (unchanged).

.. code-block:: python

    INSTALLED_APPS = [
        ...
        'django_filters',
    ]


Usage
-----

Django-filter can be used for generating interfaces similar to the Django
admin's ``list_filter`` interface.  It has an API very similar to Django's
``ModelForms``.  For example, if you had a Product model you could have a
filterset for it with the code:

.. code-block:: python

    import django_filters

    class ProductFilter(django_filters.FilterSet):
        class Meta:
            model = Product
            fields = ['name', 'price', 'manufacturer']


And then in your view you could do:

.. code-block:: python

    def product_list(request):
        filter = ProductFilter(request.GET, queryset=Product.objects.all())
        return render(request, 'my_app/template.html', {'filter': filter})


Usage with Django REST Framework
--------------------------------

Django-filter provides a custom ``FilterSet`` and filter backend for use with
Django REST Framework.

To use this adjust your import to use
``django_filters.rest_framework.FilterSet``.

.. code-block:: python

    from django_filters import rest_framework as filters

    class ProductFilter(filters.FilterSet):
        class Meta:
            model = Product
            fields = ('category', 'in_stock')


For more details see the `DRF integration docs`_.


Support
-------

If you need help you can start a `discussion`_. For commercial support, please
`contact Carlton Gibson via his website <https://noumenal.es/>`_.

.. _`discussion`: https://github.com/carltongibson/django-filter/discussions
.. _`read the docs`: https://django-filter.readthedocs.io/en/main/
.. _`DRF integration docs`: https://django-filter.readthedocs.io/en/stable/guide/rest_framework.html
