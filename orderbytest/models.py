from django.db import models


class MyModel(models.Model):
    id = models.AutoField(primary_key=True)
    time_stamp = models.DateTimeField(null=True)

    class Meta:
        ordering = [models.F('time_stamp').desc(nulls_last=True)]


class MyChildModel(MyModel):
    name = models.CharField(max_length=144)
