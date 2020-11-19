from .forms import DegreeForm, PositionForm, EmployeeForm, UploadFileForm
from .models import Degrees, Positions, Employees

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

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
    return redirect('employees:show_table', table_name=table_name)


def export_csv(request, table_name):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(table_name + '.csv')

    writer = csv_writer(response)
    writer.writerow([field.name for field in TABLES[table_name]['model']._meta.get_fields()[1:]])
    for obj in TABLES[table_name]['model'].objects.all():
        writer.writerow([getattr(obj, field.name) for field in TABLES[table_name]['model']._meta.get_fields()[1:]])
    return response


def import_csv(request, table_name):
    # POST method
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            TABLES[table_name]['model'].import_data(
                DictReader(StringIO(request.FILES['file'].read().decode('UTF-8')), delimiter=','))

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
