from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.html import format_html


class Degrees(models.Model):

    name = models.CharField(max_length=45, unique=True)

    table_name = "Degrees"
    html_columns = format_html(u"<th>Name</th>")

    def __str__(self):
        return self.name

    @staticmethod
    def import_data(csv_dict):
        for row in csv_dict:
            try:
                record = Degrees.objects.get(name=row['name'])
                record.name = row['name']
                record.save()
            except ObjectDoesNotExist:
                Degrees.objects.create(name=row['name'])

    def html_table_row(self):
        return format_html(u"<td>{0}</td>", self.name)


class Positions(models.Model):

    name = models.CharField(max_length=45, unique=True)

    table_name = "Positions"
    html_columns = format_html(u"<th>Name</th>")

    def __str__(self):
        return self.name

    @staticmethod
    def import_data(csv_dict):
        for row in csv_dict:
            try:
                record = Positions.objects.get(name=row['name'])
                record.name = row['name']
                record.save()
            except ObjectDoesNotExist:
                Positions.objects.create(name=row['name'])

    def html_table_row(self):
        return format_html(u"<td>{0}</td>", self.name)


class Employees(models.Model):

    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    abbreviation = models.CharField(max_length=5, unique=True, null=True, blank=True) # reconsider BLANK and NULL
    degree = models.ForeignKey(Degrees, on_delete=models.SET_NULL, null=True)
    position = models.ForeignKey(Positions, on_delete=models.SET_NULL, null=True, blank=True)
    e_mail = models.EmailField(max_length=45, unique=True)
    supervisor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    year_of_studies = models.PositiveSmallIntegerField(null=True, blank=True)
    is_procedure_for_a_doctoral_degree_approved = models.BooleanField(default=False)
    has_scholarship = models.BooleanField(default=False)

    table_name = "Employees"
    html_columns = format_html(u"<th>First Name</th><th>Last Name</th><th>Abbreviation</th><th>Degree</th>\
    <th>Position</th><th>E-mail</th><th>Supervisor</th><th>Year of studies</th>\
    <th>Is procedure for a doctoral degree approved</th><th>Has scholarship</th>")

    def __str__(self):
        return self.abbreviation

    @staticmethod
    def import_data(csv_dict):
        for row in csv_dict:
            try:
                record = Employees.objects.get(e_mail=row['e_mail'])
                record.first_name = row['first_name']
                record.last_name = row['last_name']
                record.abbreviation = row['abbreviation']   # unique - need to be checked!!
                if row['degree'] != '':
                    record.degree = Degrees.objects.get_or_create(name=row['degree'])[0]
                else:
                    record.degree = None
                if row['position'] != '':
                    record.position = Positions.objects.get_or_create(name=row['position'])[0]
                else:
                    record.position = None
                record.e_mail = row['e_mail']   # unique - need to be checked!!
                try:
                    record.supervisor = Employees.objects.get(abbreviation=row['abbreviation'])
                except ObjectDoesNotExist:
                    record.supervisor = None
                record.year_of_studies = row['year_of_studies']
                if row['is_procedure_for_a_doctoral_degree_approved'] == 'TRUE':
                    record.is_procedure_for_a_doctoral_degree_approved = True
                else:
                    record.is_procedure_for_a_doctoral_degree_approved = False
                if row['has_scholarship'] == 'TRUE':
                    record.has_scholarship = True
                else:
                    record.has_scholarship = False
                record.save()
            except ObjectDoesNotExist:
                record = Employees.objects.create(
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                    abbreviation=row['abbreviation'],   # unique - need to be checked!!
                    degree=Degrees.objects.get_or_create(name=row['degree'])[0] if row['degree'] != '' else None,
                    position=Positions.objects.get_or_create(name=row['position'])[0]\
                        if row['position'] != '' else None,
                    e_mail=row['e_mail'],   # unique - need to be checked!!
                    year_of_studies=row['year_of_studies'],
                    is_procedure_for_a_doctoral_degree_approved=True\
                        if row['is_procedure_for_a_doctoral_degree_approved'] == 'TRUE' else False,
                    has_scholarship=True if row['has_scholarship'] == 'TRUE' else False,
                )
                try:
                    record.supervisor = Employees.objects.get(abbreviation=row['abbreviation'])
                except ObjectDoesNotExist:
                    record.supervisor = None

    def html_table_row(self):
        empty = format_html('<span style="color: {color}"><b>-</b></span>', color='red')
        return format_html(u"<td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td>\
        <td>{6}</td><td>{7}</td><td>{8}</td><td>{9}</td>",
                           self.first_name,
                           self.last_name,
                           empty if self.abbreviation is None else self.abbreviation,
                           empty if self.degree is None else self.degree,
                           empty if self.position is None else self.position,
                           self.e_mail,
                           empty if self.supervisor is None else self.supervisor,
                           empty if self.year_of_studies is None else self.year_of_studies,
                           'Yes' if self.is_procedure_for_a_doctoral_degree_approved else 'No',
                           'Yes' if self.has_scholarship else 'No',
                           )
