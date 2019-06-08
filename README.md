# OrderBy Bug
## Description
When using a query expression for meta
[ordering](https://docs.djangoproject.com/en/2.2/ref/models/options/#django.db.models.Options.ordering)
on a parent model during a multi-table inheritance relationship causes a TypeError during
test runner serialization.

## Example Models
```python
from django.db import models


class MyModel(models.Model):
    id = models.AutoField(primary_key=True)
    time_stamp = models.DateTimeField(null=True)

    class Meta:
        ordering = [models.F('time_stamp').desc(nulls_last=True)]


class MyChildModel(MyModel):
    name = models.CharField(max_length=144)

```

## To Reproduce

- Download the repo, install Django 2.2
- run `python manage.py makemigrations` then `python manage.py migrate`
- Run `python manage.py test`
- Encounter TypeError and teh below stacktrace.

## REPL Weirdness
However, If you interact with the model in REPL or script everything works as expected!

```python
from django.utils import timezone
from orderbytest.models import MyChildModel


MyChildModel.objects.create(name='first', time_stamp=timezone.now())
MyChildModel.objects.create(name='second', time_stamp=timezone.now())
MyChildModel.objects.create(name='third', time_stamp=None)

list(MyChildModel.objects.all())[0].name == 'second'
# True
```

## Rationale

During [get_order_dir](https://github.com/django/django/blob/master/django/db/models/sql/query.py#L2201) `field`
is an OrderBy object and not a string, therefore the index fails. Strangely enough, I've only been able to
reproduce this during testing. It must have something to do with the serialization processes use of iter.

## Stack Trace
```cmd
Creating test database for alias 'default'...
Traceback (most recent call last):
  File "manage.py", line 21, in <module>
    main()
  File "manage.py", line 17, in main
    execute_from_command_line(sys.argv)
  File "E:\users\jfuller\documents\PycharmVENVs\djangoorderbytest\lib\site-packages\django\core\management\__init__.py", line 381, in execute_from_command_line
    utility.execute()
  File "E:\users\jfuller\documents\PycharmVENVs\djangoorderbytest\lib\site-packages\django\core\management\__init__.py", line 375, in execute
    self.fetch_command(subcommand).run_from_argv(self.argv)
  File "E:\users\jfuller\documents\PycharmVENVs\djangoorderbytest\lib\site-packages\django\core\management\commands\test.py", line 23, in run_from_argv
    super().run_from_argv(argv)
  File "E:\users\jfuller\documents\PycharmVENVs\djangoorderbytest\lib\site-packages\django\core\management\base.py", line 323, in run_from_argv
    self.execute(*args, **cmd_options)
  File "E:\users\jfuller\documents\PycharmVENVs\djangoorderbytest\lib\site-packages\django\core\management\base.py", line 364, in execute
    output = self.handle(*args, **options)
  File "E:\users\jfuller\documents\PycharmVENVs\djangoorderbytest\lib\site-packages\django\core\management\commands\test.py", line 53, in handle
    failures = test_runner.run_tests(test_labels)
  File "E:\users\jfuller\documents\PycharmVENVs\djangoorderbytest\lib\site-packages\django\test\runner.py", line 629, in run_tests
    old_config = self.setup_databases(aliases=databases)
  File "E:\users\jfuller\documents\PycharmVENVs\djangoorderbytest\lib\site-packages\django\test\runner.py", line 554, in setup_databases
    self.parallel, **kwargs
  File "E:\users\jfuller\documents\PycharmVENVs\djangoorderbytest\lib\site-packages\django\test\utils.py", line 174, in setup_databases
    serialize=connection.settings_dict.get('TEST', {}).get('SERIALIZE', True),
  File "E:\users\jfuller\documents\PycharmVENVs\djangoorderbytest\lib\site-packages\django\db\backends\base\creation.py", line 80, in create_test_db
    self.connection._test_serialized_contents = self.serialize_db_to_string()
  File "E:\users\jfuller\documents\PycharmVENVs\djangoorderbytest\lib\site-packages\django\db\backends\base\creation.py", line 123, in serialize_db_to_string
    serializers.serialize("json", get_objects(), indent=None, stream=out)
  File "E:\users\jfuller\documents\PycharmVENVs\djangoorderbytest\lib\site-packages\django\core\serializers\__init__.py", line 128, in serialize
    s.serialize(queryset, **options)
  File "E:\users\jfuller\documents\PycharmVENVs\djangoorderbytest\lib\site-packages\django\core\serializers\base.py", line 90, in serialize
    for count, obj in enumerate(queryset, start=1):
  File "E:\users\jfuller\documents\PycharmVENVs\djangoorderbytest\lib\site-packages\django\db\backends\base\creation.py", line 120, in get_objects
    yield from queryset.iterator()
  File "E:\users\jfuller\documents\PycharmVENVs\djangoorderbytest\lib\site-packages\django\db\models\query.py", line 341, in _iterator
    yield from self._iterable_class(self, chunked_fetch=use_chunked_fetch, chunk_size=chunk_size)
  File "E:\users\jfuller\documents\PycharmVENVs\djangoorderbytest\lib\site-packages\django\db\models\query.py", line 55, in __iter__
    results = compiler.execute_sql(chunked_fetch=self.chunked_fetch, chunk_size=self.chunk_size)
  File "E:\users\jfuller\documents\PycharmVENVs\djangoorderbytest\lib\site-packages\django\db\models\sql\compiler.py", line 1087, in execute_sql
    sql, params = self.as_sql()
  File "E:\users\jfuller\documents\PycharmVENVs\djangoorderbytest\lib\site-packages\django\db\models\sql\compiler.py", line 474, in as_sql
    extra_select, order_by, group_by = self.pre_sql_setup()
  File "E:\users\jfuller\documents\PycharmVENVs\djangoorderbytest\lib\site-packages\django\db\models\sql\compiler.py", line 55, in pre_sql_setup
    order_by = self.get_order_by()
  File "E:\users\jfuller\documents\PycharmVENVs\djangoorderbytest\lib\site-packages\django\db\models\sql\compiler.py", line 330, in get_order_by
    field, self.query.get_meta(), default_order=asc))
  File "E:\users\jfuller\documents\PycharmVENVs\djangoorderbytest\lib\site-packages\django\db\models\sql\compiler.py", line 720, in find_ordering_name
    order, already_seen))
  File "E:\users\jfuller\documents\PycharmVENVs\djangoorderbytest\lib\site-packages\django\db\models\sql\compiler.py", line 701, in find_ordering_name
    name, order = get_order_dir(name, default_order)
  File "E:\users\jfuller\documents\PycharmVENVs\djangoorderbytest\lib\site-packages\django\db\models\sql\query.py", line 2154, in get_order_dir
    if field[0] == '-':
TypeError: 'OrderBy' object does not support indexing

```

## Fix
Someone whom understands why the above works in repl/script but fails during serialization can probably crack this one.
I know it occurs because field is expected to be an index sliceable string, not an OrderBy object, but I cannot
figure out why it is an object during test and works otherwise.
