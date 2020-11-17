from django.db import models
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


class Employees(models.Model):
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    abbreviation = models.CharField(max_length=5, null=True, blank=True)
    degree = models.ForeignKey(Degrees, on_delete=models.SET_NULL, null=True)
    position = models.ForeignKey(Positions, on_delete=models.SET_NULL, null=True, blank=True)
    e_mail = models.EmailField(max_length=45)
    supervisor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    year_of_studies = models.PositiveSmallIntegerField(null=True, blank=True)
    is_procedure_for_a_doctoral_degree_approved = models.BooleanField(default=False)
    has_scholarship = models.BooleanField(default=False)

    table_name = "Employees"
    html_columns = format_html(u"<th>First Name</th><th>Last Name</th><th>Abbreviation</th><th>Degree</th>\
    <th>Position</th><th>E-mail</th><th>Supervisor</th><th>Year of studies</th>\
    <th>Is procedure for a doctoral degree approved</th><th>Has scholarship</th>")

    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name)

    def html_table_row(self):
        return format_html(u"<td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td>\
        <td>{6}</td><td>{7}</td><td>{8}</td><td>{9}</td>",
                           self.first_name,
                           self.last_name,
                           '-' if self.abbreviation is None else self.abbreviation,
                           self.degree,
                           '-' if self.position is None else self.position,
                           self.e_mail,
                           '-' if self.supervisor is None else self.supervisor,
                           '-' if self.year_of_studies is None else self.year_of_studies,
                           'Yes' if self.is_procedure_for_a_doctoral_degree_approved else 'No',
                           'Yes' if self.has_scholarship else 'No',
                           )
