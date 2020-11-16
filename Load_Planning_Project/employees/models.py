from django.db import models
from django.http import HttpResponse
from django.utils.html import format_html


class Degrees(models.Model):
    name = models.CharField(max_length=45, unique=True)

    table_name = "Degrees"
    html_columns = format_html(u"<th>Name</th>")

    def __str__(self):
        return self.name

    def html_table_row(self):
        return format_html(u"<td>{0}</td>", self.name)


class Positions(models.Model):
    name = models.CharField(max_length=45, unique=True)

    table_name = "Positions"
    html_columns = format_html(u"<th>Name</th>")

    def __str__(self):
        return self.name

    def html_table_row(self):
        return format_html(u"<td>{0}</td>", self.name)

