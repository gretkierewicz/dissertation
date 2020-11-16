from .forms import DegreeForm, PositionForm
from .models import Degrees, Positions
from django.shortcuts import render, get_object_or_404, redirect

TABLES = {
    'Degrees': {'model': Degrees, 'form': DegreeForm},
    'Positions': {'model': Positions, 'form': PositionForm},
}


def show_table(request, table_name='Degrees'):
    context = {
        'table_name': TABLES[table_name]['model'].table_name,
        'columns': TABLES[table_name]['model'].html_columns,
        'objects': TABLES[table_name]['model'].objects.all().order_by('name'),
    }
    return render(request, 'employees/index.html', context)


def new_record(request, table_name):
    # POST method
    if request.method == 'POST':
        form = TABLES[table_name]['form'](request.POST)
        if form.is_valid():
            record_check = TABLES[table_name]['model'].objects.filter(name=form.instance.name).first()
            if record_check is None:
                form.save()
        return redirect('employees:show_table')

    # GET method
    else:
        context = {
            'table_name': TABLES[table_name]['model'].table_name,
            'columns': TABLES[table_name]['model'].html_columns,
            'objects': TABLES[table_name]['model'].objects.all().order_by('name'),
            'new_flag': True,
            'form': TABLES[table_name]['form'](),
        }
        return render(request, 'employees/index.html', context)


def edit_record(request, table_name, object_id):
    record = get_object_or_404(TABLES[table_name]['model'], pk=object_id)

    # POST method
    if request.method == 'POST':
        record_from_form = TABLES[table_name]['model']()
        form = TABLES[table_name]['form'](request.POST, instance=record_from_form)
        if form.is_valid():
            record.name = record_from_form.name
            record.save()
            return redirect('employees:show_table')

        return redirect('employees:show_table')

    # GET method
    else:
        context = {
            'table_name': TABLES[table_name]['model'].table_name,
            'columns': TABLES[table_name]['model'].html_columns,
            'objects': TABLES[table_name]['model'].objects.all().order_by('name'),
            'object_id': object_id,
            'form': TABLES[table_name]['form'](initial={
                'name': record.name,
            }),
        }
    return render(request, 'employees/index.html', context)


def del_record(request, table_name, object_id):
    record = get_object_or_404(TABLES[table_name]['model'], pk=object_id)
    if record:
        record.delete()
    return redirect('employees:show_table')
