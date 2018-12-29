from tkinter import *
from tkinter.filedialog import askdirectory
import tkinter.messagebox as messagebox
import hashlib
import shutil
import time
import os
import threading
import win32file, win32con


class copy_file_threading(threading.Thread):
    def __init__(self, source_path, target_path, schedule_text, button, file_number, nobak_log_file):
        threading.Thread.__init__(self)
        self.source_path = source_path
        self.target_path = target_path
        self.schedule_text = schedule_text
        self.button = button
        self.file_number = file_number
        self.nobak_log_file = nobak_log_file
        self.update_fre = round(file_number / 100 + 1)

    def run(self):
        file_cnt = 0
        nobak_file_list = []
        self.button['state'] = 'disabled'
        for sroot_path, dirs, files in os.walk(self.source_path):
            target_dir = self.target_path + sroot_path.replace(self.source_path, '')
            if os.path.exists(target_dir):
                check_file = True
            else:
                check_file = False
                os.mkdir(target_dir)
            for file in files:
                source_file_path = os.path.join(sroot_path, file)
                target_file_path = os.path.join(target_dir, file)
                if isHidenFile(source_file_path):
                    continue
                file_cnt += 1
                if file_cnt % self.update_fre == 0:
                    self.schedule_text.set(str(round(100 * file_cnt / self.file_number, 1)) + "%")
                    self.button.update()
                if check_file:
                    if os.path.exists(target_file_path):
                        if os.path.getsize(source_file_path) > 1024 ** 3:
                            nobak_file_list += [source_file_path]
                            continue
                        source_md5 = file_md5(source_file_path)
                        target_md5 = file_md5(target_file_path)
                        if target_md5 == source_md5:
                            print("pass!")
                            continue
                # time.sleep(1)
                shutil.copyfile(source_file_path, target_file_path)
        if len(nobak_file_list):
            with open(self.nobak_log_file, 'w') as log:
                for file in nobak_file_list:
                    log.write(file + '\r\n')
            messagebox.showwarning('大文件警告', '存在{}个大文件（超过1G）在源路径和目标路径均已经存在，为节省时间没有备份。文件清单已经保存为日志：{}，请查看！'.format(
                len(nobak_file_list), self.nobak_log_file))
        else:
            messagebox.showinfo('备份完成', '备份已经完成！请检查你的文件！')
        self.button['state'] = 'normal'
        self.schedule_text.set("开始备份")


class count_file_threading(threading.Thread):
    def __init__(self, source_path, source_btn, target_btn):
        threading.Thread.__init__(self)
        self.source_path = source_path
        self.source_btn = source_btn
        self.target_btn = target_btn

    def run(self):
        self.source_btn['state'] = 'disabled'
        self.target_btn['state'] = 'disabled'
        num = count_number_of_files(self.source_path)
        messagebox.showinfo('路径文件统计结果', '路径下文件总数：{}'.format(num))
        self.source_btn['state'] = 'normal'
        self.target_btn['state'] = 'normal'


def isHidenFile(filePath):
    fileAttr = win32file.GetFileAttributes(filePath)
    if fileAttr & win32con.FILE_ATTRIBUTE_HIDDEN:
        return True
    return False


def file_md5(file_path):
    m = hashlib.md5()
    with open(file_path, 'rb') as file:
        while True:
            data = file.read(10240)
            if not data:
                break
            m.update(data)
    return m.hexdigest()


def count_number_of_files(source_path):
    file_number = 0
    for sroot_path, dirs, files in os.walk(source_path):
        for file in files:
            if not isHidenFile(os.path.join(sroot_path, file)):
                file_number += 1
    return file_number


def select_path(path):
    _path = askdirectory()
    path.set(_path)


class backup_data_class(object):
    def __init__(self):
        self.window = Tk()
        self.window.title("硬盘增量备份助手v1.0")
        Label(self.window, text='需要备份的源路径：', font=('宋体', 12), width=20, height=2, anchor=W).grid(row=0, column=0)
        self.source_path = StringVar()
        Entry(self.window, textvariable=self.source_path).grid(row=0, column=1)
        Button(self.window, text='选择路径', font=('宋体', 12), command=lambda: select_path(self.source_path)).grid(row=0,
                                                                                                              column=2)

        Label(self.window, text='需要备份的目标路径：', font=('宋体', 12), width=20, height=2).grid(row=1, column=0)
        self.target_path = StringVar()
        Entry(self.window, textvariable=self.target_path).grid(row=1, column=1)
        Button(self.window, text='选择路径', font=('宋体', 12), command=lambda: select_path(self.target_path)).grid(row=1,
                                                                                                              column=2)

        self.count_source_btn = Button(self.window, text='统计源路径文件数', font=('宋体', 12),
                                       command=lambda: self.count_files_and_report(self.source_path.get()))
        self.count_source_btn.grid(row=3, column=0)
        self.count_target_btn = Button(self.window, text='统计目标路径文件数', font=('宋体', 12),
                                       command=lambda: self.count_files_and_report(self.target_path.get()))
        self.count_target_btn.grid(row=3, column=2)

        self.start_btn_text = StringVar()
        self.start_btn_text.set("开始备份")
        self.start_btn = Button(self.window, textvariable=self.start_btn_text, font=('宋体', 12),
                                command=lambda: self.start_backup(self.source_path.get(), self.target_path.get()))
        self.start_btn.grid(row=3, column=1)
        Label(self.window, text='作者：小武', font=('宋体', 12), width=20, height=2).grid(row=4, column=0)
        Label(self.window, text='Bug反馈QQ：453598288', font=('宋体', 12), width=20, height=2).grid(row=4, column=1)
        Label(self.window,
              text='使用说明：该程序用于将你本地的某个目录映射到你移动硬盘的某个目录，程序会自动同步这两个目录下的所有文件，如果发现已经存在的文件会对这两个文件进行对比，不同则执行拷贝，相同则跳过。',
              font=('宋体', 12), width=60, height=4, wraplength=480, anchor='w', justify='left').grid(row=5, column=0,
                                                                                                    sticky=W,
                                                                                                    columnspan=3,
                                                                                                    rowspan=2)
        self.window.mainloop()

    def start_backup(self, source_path, target_path):
        if len(source_path) < 1 or not os.path.exists(source_path):
            messagebox.showerror('错误', '没有选择有效源路径！请检查！')
            return None
        if len(target_path) < 1 or not os.path.exists(target_path):
            messagebox.showerror('错误', '没有选择目标路径！')
            return None
        file_number = count_number_of_files(source_path)
        start_bak = messagebox.askyesno('文件数量统计', '需要备份的总文件数量：{}\n开始执行备份？'.format(file_number))
        nobak_log_file = time.strftime('./no-backup-log-%m-%d---%H-%M-%S.txt', time.localtime(time.time()))
        if start_bak:
            t = copy_file_threading(source_path, target_path, self.start_btn_text, self.start_btn, file_number,
                                    nobak_log_file)
            t.start()

    def count_files_and_report(self, source_path):
        if len(source_path) < 1 or not os.path.exists(source_path):
            messagebox.showerror('错误', '没有选择有效路径！请检查！')
            return None
        t = count_file_threading(source_path, self.count_source_btn, self.count_target_btn)
        t.start()
        return None


def main():
    temp = backup_data_class()


if __name__ == '__main__':
    main()
    # st = time.time()
    # md5test = file_md5(r'C:\迅雷下载\[DYGC.ORG]李茶的姑妈.Hello.Mrs.Money.2018.4K.1080P.WEB-DL.X264.AAC.Mandarin.CHS.ENG-DYGC\[DYGC.ORG]李茶的姑妈.Hello.Mrs.Money.2018.1080P.WEB-DL.X264.AAC.Mandarin.CHS.ENG-DYGC.mp4')
    # print("time:", time.time() - st)
    # print("md5:", md5test)
