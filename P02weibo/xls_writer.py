import os.path

import xlwt


class XlsWriter(object):
    _entered = False

    def __init__(self, file_name, headers=None):
        self.file_name = file_name
        if not os.path.exists(file_name):
            with open(file_name, 'w'):
                pass
        self.workbook = xlwt.Workbook()
        self.sheet = self.workbook.add_sheet("Sheet1")
        self.headers = []
        self.column_count = 0
        if headers:
            self.set_headers(headers)

    def __enter__(self):
        self._entered = True  # 标记已进入上下文管理器
        self.build_headers()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save_file()
        self._entered = False  # 重置标志
        if exc_type:
            raise RuntimeError("An error occurred while working with the Excel file")

    def _ensure_entered(self):
        """确保已通过上下文管理器进入实例"""
        if not self._entered:
            raise RuntimeError("This instance must be used as a context manager.")

    def set_headers(self, headers):
        self.headers = headers
        self.column_count = len(headers)

    def build_headers(self):
        self._ensure_entered()  # 添加检查
        for col_num, header in enumerate(self.headers):
            self.sheet.write(0, col_num, header)

    def add_column(self, column_name):
        self._ensure_entered()  # 添加检查
        if column_name in self.headers:
            raise ValueError(f"Column '{column_name}' already exists.")
        self.headers.append(column_name)
        self.sheet.write(0, self.column_count, column_name)
        self.column_count += 1

    def add_item(self, item):
        self._ensure_entered()  # 添加检查
        if len(item) != self.column_count:
            raise ValueError("Item length does not match the number of columns.")
        row_num = self.sheet.last_used_row + 1
        for col_num, value in enumerate(item):
            self.sheet.write(row_num, col_num, value)

    def save_file(self):
        """仅在退出时调用，无需外部调用检查"""
        self.workbook.save(self.file_name)
