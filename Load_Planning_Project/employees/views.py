from .forms import DegreeForm, PositionForm, EmployeeForm, UploadFileForm
from .models import Degrees, Positions, Employees

from django.contrib import messages
from django.contrib.messages import add_message
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.html import format_html

from csv import DictReader
from csv import writer as csv_writer
from io import StringIO


TABLES = {
    'Degrees': {'model': Degrees, 'form': DegreeForm},
    'Positions': {'model': Positions, 'form': PositionForm},
    'Employees': {'model': Employees, 'form': EmployeeForm},
}


def show_table(request, table_name='Degrees'):
    context = {
        'table_name': TABLES[table_name]['model'].table_name,
        'columns': TABLES[table_name]['model'].html_columns,
        'objects': TABLES[table_name]['model'].objects.all(),
    }
    return render(request, 'employees/index.html', context)


def new_record(request, table_name):
    # POST method
    if request.method == 'POST':
        form = TABLES[table_name]['form'](request.POST)
        if form.is_valid():
            form.save()
            add_message(request, messages.INFO,
                        format_html(u'Record <span style="color: green;"><b>created</b></span> successfully.'))
        return redirect('employees:show_table', table_name=table_name)

    # GET method
    else:
        context = {
            'table_name': TABLES[table_name]['model'].table_name,
            'columns': TABLES[table_name]['model'].html_columns,
            'objects': TABLES[table_name]['model'].objects.all(),
            'new_record_flag': True,
            'form': TABLES[table_name]['form'](),
        }
        return render(request, 'employees/index.html', context)


def edit_record(request, table_name, object_id):
    record = get_object_or_404(TABLES[table_name]['model'], pk=object_id)

    # POST method
    if request.method == 'POST':
        form = TABLES[table_name]['form'](request.POST, instance=record)
        if form.is_valid():
            form.save()
            add_message(request, messages.INFO,
                        format_html(u'Record <span style="color: blue;"><b>edited</b></span> successfully.'))
            return redirect('employees:show_table', table_name=table_name)

        return redirect('employees:show_table', table_name=table_name)

    # GET method
    else:
        context = {
            'table_name': TABLES[table_name]['model'].table_name,
            'columns': TABLES[table_name]['model'].html_columns,
            'objects': TABLES[table_name]['model'].objects.all(),
            'object_id': object_id,
            'form': TABLES[table_name]['form'](instance=record),
        }
    return render(request, 'employees/index.html', context)


def del_record(request, table_name, object_id):
    record = get_object_or_404(TABLES[table_name]['model'], pk=object_id)
    if record:
        record.delete()
        add_message(request, messages.INFO,
                    format_html(u'Record <span style="color: red;"><b>deleted</b></span> successfully.'))
    return redirect('employees:show_table', table_name=table_name)


def export_csv(request, table_name):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(table_name + '.csv')

    writer = csv_writer(response)
    writer.writerow([field.name for field in TABLES[table_name]['model']._meta.get_fields()[2:]])
    for obj in TABLES[table_name]['model'].objects.all():
        writer.writerow([getattr(obj, field.name) for field in TABLES[table_name]['model']._meta.get_fields()[2:]])
    return response


def import_csv(request, table_name):
    # POST method
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        msg_table = []
        if form.is_valid():
            msg_table = TABLES[table_name]['model'].import_data(
                DictReader(StringIO(request.FILES['file'].read().decode('UTF-8')), delimiter=','))
        for msg in msg_table:
            add_message(request, messages.INFO, msg)
        return redirect('employees:show_table', table_name=table_name)

    # GET method
    else:
        context = {
            'table_name': TABLES[table_name]['model'].table_name,
            'columns': TABLES[table_name]['model'].html_columns,
            'objects': TABLES[table_name]['model'].objects.all(),
            'import_csv_flag': True,
            'form': UploadFileForm(),
        }
        return render(request, 'employees/index.html', context)
