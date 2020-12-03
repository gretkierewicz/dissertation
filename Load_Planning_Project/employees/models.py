from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.html import format_html


class Degrees(models.Model):
    name = models.CharField(max_length=45, unique=True)

    def __str__(self):
        return self.name

    @staticmethod
    def import_data(csv_dict):
        msg_table = [format_html(u'<span style="color: blue;"><b>Imported data log:</b></span><br>')]
        for row in csv_dict:
            try:
                record = Degrees.objects.get(name=row['name'])
                msg_table.append(format_html(u'Record already exists: <b>{0}</b>'.format(record.name)))
            except ObjectDoesNotExist:
                if format_html('<br><b>New entries:</b>') not in msg_table:
                    msg_table.append(format_html('<br><b>New entries:</b>'))
                Degrees.objects.create(name=row['name'])
                msg_table.append(format_html(u'Record created: <b>{0}</b>'.format(row['name'])))
        return msg_table


class Positions(models.Model):
    name = models.CharField(max_length=45, unique=True)

    def __str__(self):
        return self.name

    @staticmethod
    def import_data(csv_dict):
        msg_table = [format_html(u'<span style="color: blue;"><b>Imported data log:</b></span><br>')]
        for row in csv_dict:
            try:
                record = Positions.objects.get(name=row['name'])
                msg_table.append(format_html(u'Record already exists: <b>{0}</b>'.format(record.name)))
            except ObjectDoesNotExist:
                if format_html('<br><b>New entries:</b>') not in msg_table:
                    msg_table.append(format_html('<br><b>New entries:</b>'))
                Positions.objects.create(name=row['name'])
                msg_table.append(format_html(u'Record created: <b>{0}</b>'.format(row['name'])))
        return msg_table


class Employees(models.Model):
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    abbreviation = models.CharField(max_length=5, unique=True)
    degree = models.ForeignKey(Degrees, on_delete=models.SET_NULL, null=True)
    position = models.ForeignKey(Positions, on_delete=models.SET_NULL, null=True)
    e_mail = models.EmailField(max_length=45, unique=True)
    supervisor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    year_of_studies = models.PositiveSmallIntegerField(null=True, blank=True)
    is_procedure_for_a_doctoral_degree_approved = models.BooleanField(default=False)
    has_scholarship = models.BooleanField(default=False)

    def __str__(self):
        return self.abbreviation

    @staticmethod
    def import_data(csv_dict):
        msg_table = [format_html(u'<span style="color: blue;"><b>Imported data log:</b></span><br>')]
        import_emails = []
        for row in csv_dict:
            try:
                record = Employees.objects.get(e_mail=row['e_mail'])
                edited = False
                if row['e_mail'] in import_emails:
                    # if e-mail occurs more than once in imported table
                    raise ObjectDoesNotExist
                import_emails.append(row['e_mail'])
                if record.first_name != row['first_name']:
                    record.first_name = row['first_name']
                    edited = True
                if record.last_name != row['last_name']:
                    record.last_name = row['last_name']
                    edited = True
                if record.abbreviation != row['abbreviation']:
                    try:
                        Employees.objects.get(abbreviation=row['abbreviation'])
                    except ObjectDoesNotExist:
                        record.abbreviation = row['abbreviation']
                        edited = True
                if getattr(record.degree, 'name', '') != row['degree']:
                    if row['degree'] != '':
                        try:
                            record.degree = Degrees.objects.get(name=row['degree'])
                        except ObjectDoesNotExist:
                            record.degree = Degrees.objects.create(name=row['degree'])
                    else:
                        record.degree = None
                    edited = True
                if getattr(record.position, 'name', '') != row['position']:
                    if row['position'] != '':
                        try:
                            record.position = Positions.objects.get(name=row['position'])
                        except ObjectDoesNotExist:
                            record.position = Positions.objects.create(name=row['position'])
                    else:
                        record.position = None
                    edited = True
                if getattr(record.supervisor, 'abbreviation', '') != row['supervisor']:
                    try:
                        record.supervisor = Employees.objects.get(abbreviation=row['supervisor'])
                    except ObjectDoesNotExist:
                        record.supervisor = None
                    edited = True
                try:
                    int(row['year_of_studies'])
                    if record.year_of_studies != int(row['year_of_studies']):
                        record.year_of_studies = int(row['year_of_studies'])
                        edited = True
                except ValueError:
                    if row['year_of_studies'] != '':
                        msg_table.append(format_html(
                            u'Wrong format for "Year of studies" field for record: '
                            u'<b>{0} {1} ({2} / {3})</b>. Should be integer, got: <b>"{4}"</b>.'.format(
                                record.first_name, record.last_name, record.abbreviation, record.e_mail,
                                row['year_of_studies'])))
                if row['is_procedure_for_a_doctoral_degree_approved'] == 'TRUE':
                    if not record.is_procedure_for_a_doctoral_degree_approved:
                        record.is_procedure_for_a_doctoral_degree_approved = True
                        edited = True
                elif row['is_procedure_for_a_doctoral_degree_approved'] == 'FALSE' \
                        or row['is_procedure_for_a_doctoral_degree_approved'] == '':
                    if record.is_procedure_for_a_doctoral_degree_approved:
                        record.is_procedure_for_a_doctoral_degree_approved = True
                        edited = True
                if row['has_scholarship'] == 'TRUE':
                    if not record.has_scholarship:
                        record.has_scholarship = True
                        edited = True
                elif row['has_scholarship'] == 'FALSE' or row['has_scholarship'] == '':
                    if record.has_scholarship:
                        record.has_scholarship = False
                        edited = True
                if edited:
                    record.save()
                    msg_table.append(format_html(u'Record edited for: <b>{0} {1} ({2} / {3})</b>'.format(
                        record.first_name, record.last_name, record.abbreviation, record.e_mail)))
                else:
                    msg_table.append(format_html(u'No changes provided for: <b>{0} {1} ({2} / {3})</b>'.format(
                        record.first_name, record.last_name, record.abbreviation, record.e_mail)))

            except ObjectDoesNotExist:
                if format_html('<br><b>New entries:</b>') not in msg_table:
                    msg_table.append(format_html('<br><b>New entries:</b>'))
                try:
                    Employees.objects.get(abbreviation=row['abbreviation'])
                    msg_table.append(format_html(
                        u'Abbreviation for entry: <b>{0} {1} ({2} / {3})</b>) already in use. '
                        u'<span style="color: red;"><b>Could not create new record!</b></span>'.format(
                            row['first_name'], row['last_name'], row['abbreviation'], row['e_mail'],
                            row['year_of_studies'])))
                    abbreviation = None
                except ObjectDoesNotExist:
                    abbreviation = row['abbreviation']
                try:
                    Employees.objects.get(e_mail=row['e_mail'])
                    msg_table.append(format_html(
                        u'E-mail for entry: <b>{0} {1} ({2} / {3})</b>) already in use. '
                        u'<span style="color: red;"><b>Could not create new record!</b></span>'.format(
                            row['first_name'], row['last_name'], row['abbreviation'], row['e_mail'],
                            row['year_of_studies'])))
                    e_mail = None
                except ObjectDoesNotExist:
                    e_mail = row['e_mail']
                try:
                    years = int(row['year_of_studies'])
                except ValueError:
                    if row['year_of_studies'] != '':
                        msg_table.append(format_html(
                            u'Wrong format for "Year of studies" field for record: '
                            u'<b>{0} {1} ({2} / {3})</b>. Should be integer, got: <b>"{4}"</b>.'.format(
                                row['first_name'], row['last_name'], abbreviation, e_mail,
                                row['year_of_studies'])))
                    years = None
                if abbreviation and e_mail:
                    record = Employees.objects.create(
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        abbreviation=abbreviation,
                        degree=Degrees.objects.get_or_create(name=row['degree'])[0] if row['degree'] != '' else None,
                        position=Positions.objects.get_or_create(name=row['position'])[0] if
                        row['position'] != '' else None,
                        e_mail=e_mail,
                        year_of_studies=years,
                        is_procedure_for_a_doctoral_degree_approved=True if
                        row['is_procedure_for_a_doctoral_degree_approved'] == 'TRUE' else False,
                        has_scholarship=True if row['has_scholarship'] == 'TRUE' else False,
                    )
                    try:
                        record.supervisor = Employees.objects.get(abbreviation=row['supervisor'])
                    except ObjectDoesNotExist:
                        record.supervisor = None
        return msg_table
