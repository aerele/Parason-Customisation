# Copyright (c) 2022, Aerele Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, date
from parason_customization.custom_py.attendance import create_attendance

class ShortLeaveRequest(Document):
	def validate(self):
		from_time = datetime.strptime(self.from_time, '%Y-%m-%d %H:%M:%S')
		to_time = datetime.strptime(self.to_time, '%Y-%m-%d %H:%M:%S')
		short_leave_mins = frappe.utils.time_diff_in_seconds(to_time, from_time)/60

		short_leave_limit = int(frappe.db.get_value("Attendance Settings", "Attendance Settings", "short_leave_limit")) / 60
		if short_leave_mins > short_leave_limit:
			frappe.throw("Not allowed to apply for more than 2 hours")
		application_for_month = 0

		last_day = frappe.utils.data.get_last_day(str(self.from_time).split(" ")[0]).day
		month_begin = frappe.utils.getdate(self.from_time).replace(day=1)
		month_end = frappe.utils.getdate(self.from_time).replace(day=last_day)

		duplicate = [self.name]
		found = 0
		docs = frappe.get_list(self.doctype, {"employee": self.employee, "from_time": ["between", [month_begin, month_end]], "name": ["not in", duplicate]})
		for doc in docs:
			if doc.name != self.name:
				frappe.throw("You're already consumed the request for this month")
		attendance = None
		attendance = frappe.db.get_values("Attendance", {"employee": self.employee, "attendance_date": frappe.utils.getdate(self.from_time)}, ["status", "in_time", "out_time"])

		if attendance:

			self.attendance = attendance[0].status
			self.logs = []

	def on_submit(self):
		start = datetime.strptime(self.start_date.date(), "%Y-%m-%d")
		if start < date.today():
			create_attendance(self.employee, start.date())
