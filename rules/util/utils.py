#!/usr/bin/env python
# encoding: utf-8

import traceback
import StringIO

def get_tb_info():
    fp = StringIO.StringIO()  # 创建内存文件对象
    traceback.print_exc(file=fp)
    message = fp.getvalue()
    return message
