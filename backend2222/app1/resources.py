from import_export import resources, fields
from .models import BiometricAttendance

class BiometricAttendanceResource(resources.ModelResource):
    sr_no = fields.Field(column_name='Sr.No.', attribute='sr_no')
    pay_code = fields.Field(column_name='PayCode', attribute='pay_code')
    card_no = fields.Field(column_name='Card No', attribute='card_no')
    employee_name = fields.Field(column_name='Employee Name', attribute='employee_name')
    department = fields.Field(column_name='Department', attribute='department')
    designation = fields.Field(column_name='Designation', attribute='designation')
    shift = fields.Field(column_name='Shift', attribute='shift')
    start = fields.Field(column_name='Start', attribute='start')
    in_time = fields.Field(column_name='In', attribute='in_time')
    out_time = fields.Field(column_name='Out', attribute='out_time')
    hrs_works = fields.Field(column_name='Hrs Works', attribute='hrs_works')
    status = fields.Field(column_name='Status', attribute='status')
    early_arrival = fields.Field(column_name='Early Arriv.', attribute='early_arrival')
    late_arrival = fields.Field(column_name='Late Arriv.', attribute='late_arrival')
    shift_early = fields.Field(column_name='Shift Early', attribute='shift_early')
    excess_lunch = fields.Field(column_name='Excess Lunch', attribute='excess_lunch')
    ot = fields.Field(column_name='Ot', attribute='ot')
    ot_amount = fields.Field(column_name='Ot Amount', attribute='ot_amount')
    manual = fields.Field(column_name='Manual', attribute='manual')

    class Meta:
        model = BiometricAttendance
        import_id_fields = ['card_no']

    def before_import_row(self, row, **kwargs):
        # Strip leading/trailing spaces from column names
        keys = list(row.keys())
        for key in keys:
            trimmed_key = key.strip()
            if trimmed_key != key:
                row[trimmed_key] = row.pop(key)
