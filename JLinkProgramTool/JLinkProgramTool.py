#-*- encoding=UTF-8 -*-
__version__ = 'v10'

import re

import pylink
import os
import time
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import MyThread

# pylink-squarek库使用JLinkARM.dll文件驱动J-Link，JLinkARM.dll文件可在J-Link驱动目录下找到，J-Link驱动必须是V6.0版本以上
# 这里优先选择工具目录下的JLinkARM.dll，本工具自带的JLinkARM.dll版本为V6.20d
# jlink_dll_path变量为JLinkARM.dll的路径，如果为None则自动寻找jlink驱动的安装路径
if os.path.exists('JLink_x64.dll'):
   jlink_dll_path = 'JLink_x64.dll'
else:
   jlink_dll_path = None

#烧录的文件路径
file = None

#设置Label的内容
def SetJlinkInfoLabel(label, text, color='black'):
    if label is not None:
        label.config(fg=color, text=text)

#烧录回调函数，用于获取当前操作的动作和百分比
def progress(action, progress_string, percentage):
   global info
   if action == b'Program':
      if percentage != 100:
         SetJlinkInfoLabel(info, '%d%%' % percentage)
      else:
         SetJlinkInfoLabel(info, '烧录完成')

#获取通过USB连接的J-Link列表
def GetJlinkUsbList():
   jlink_list = []

   info = pylink.JLink(lib=pylink.library.Library(dllpath=jlink_dll_path)).\
      connected_emulators(host=pylink.enums.JLinkHost.USB)
   for i in info:
      jlink_list += re.findall(r"\d+\.?\d*", str(i))
   return jlink_list

#更新J-Link列表
def JlinkSelectComboboxUpdate(event=None):
   global selectCombobox
   selectCombobox['values'] = GetJlinkUsbList()

#选择烧录文件
def SelectFile():
   global file
   file = filedialog.askopenfilename(initialdir=os.getcwd(),
                                     title=u"选择烧录文件", filetypes=[('hex files', '.hex'), ('bin files', '.bin'),
                                                                 ('All', '*.*')])
   print('选择文件%s' % file)

#进入烧录状态
def EntryFlashMode():
   flashButton.config(state=DISABLED)
   filemenu.entryconfig(0, state=DISABLED)

#退出烧录状态
def ExitFlashMode():
   flashButton.config(state=NORMAL)
   filemenu.entryconfig(0, state=NORMAL)

#烧录线程
def FLashThread(JLinkNo, chip, file, addr, info=None):
   EntryFlashMode()

   ticks = time.time()

   SetJlinkInfoLabel(info, '开始烧录')

   jlink = pylink.JLink(lib=pylink.library.Library(dllpath=jlink_dll_path))
   jlink.open(JLinkNo)
   jlink.set_tif(pylink.enums.JLinkInterfaces.SWD)
   #连接芯片
   jlink.connect(chip, speed=8000, verbose=True)
   # jlink.set_reset_strategy(pylink.enums.JLinkResetStrategyCortexM3.RESETPIN)

   #读取芯片信息
   # SetJlinkInfoLabel(info, 'ARM Id: %d, CPU Id: %d, Core Name: %s, Device Family: %d'
   #                   % (jlink.core_id(), jlink.core_cpu(), jlink.core_name(), jlink.device_family()), 'blue')
   print('ARM Id: %d' % jlink.core_id())
   print('CPU Id: %d' % jlink.core_cpu())
   print('Core Name: %s' % jlink.core_name())
   print('Device Family: %d' % jlink.device_family())

   #整片擦除
   # jlink.erase()

   #烧录文件
   flag = True
   try:
      jlink.flash_file(file, addr, on_progress=progress)
   except:
      flag = False

   jlink.reset()
   jlink.close()

   ticks = int(time.time() - ticks)
   if flag:
      SetJlinkInfoLabel(info, '烧录完成' + '，用时' + str(ticks) + '秒', 'green')
   else:
      SetJlinkInfoLabel(info, '烧录失败', 'red')

   ExitFlashMode()

#开始烧录
def StartFlash(info):
   global file
   if not jlinkNo.get() in GetJlinkUsbList():
      SetJlinkInfoLabel(info, '请选择正确的J-Link序列号', 'red')
      return
   if chip.get() == '':
      SetJlinkInfoLabel(info, '请输入芯片型号', 'red')
      return
   if addr.get() == '':
      SetJlinkInfoLabel(info, '请输入烧录地址', 'red')
      return
   if file is None:
      SetJlinkInfoLabel(info, '请选择烧录文件', 'red')
      return

   Thread = MyThread.MyThread(func=FLashThread, args=(jlinkNo.get(), chip.get(), file, addr.get(), info, ))
   Thread.setDaemon(True)
   Thread.start()

if __name__ == '__main__':
   #以下是界面相关的代码
   root = Tk(className=' J-Link烧录工具 ' + __version__)
   root.resizable(width=False, height=False)

   menubar = Menu(root)
   filemenu = Menu(menubar, tearoff=0)
   filemenu.add_command(label="选择文件", command=SelectFile)
   menubar.add_cascade(label="文件", menu=filemenu)

   helpmenu = Menu(menubar, tearoff=0)
   helpmenu.add_command(label="关于", command=lambda: messagebox.showinfo("关于", '作者：5265325\n版本：' + __version__ + '\n版权所有，翻版不究'))
   menubar.add_cascade(label="帮助", menu=helpmenu)

   root.config(menu=menubar)

   body = Frame(root)

   Label(body, text='J-Link序列号').grid(padx=4, pady=2, row=0, column=0, sticky='S' + 'N' + 'E' + 'W')
   jlinkNo = StringVar()
   selectCombobox = ttk.Combobox(body, textvariable=jlinkNo, width=10)
   selectCombobox['values'] = GetJlinkUsbList()
   if selectCombobox['values'] != ():
      jlinkNo.set(selectCombobox['values'][0])
   selectCombobox.grid(row=0, column=1, sticky='E' + 'W')
   selectCombobox.bind('<Button-1>', JlinkSelectComboboxUpdate)

   #默认的芯片型号
   # chip = StringVar(value='STM32L476RG')
   chip = StringVar(value='Cortex-M3')
   Label(body, text='芯片型号').grid(padx=4, pady=2, row=0, column=2, sticky='S' + 'N' + 'E' + 'W')
   Entry(body, textvariable=chip, width=12).grid(padx=4, pady=2, row=0, column=3, sticky='S' + 'N' + 'E' + 'W')

   #默认的烧录地址
   addr = StringVar(value='0x8000000')
   Label(body, text='烧录地址').grid(padx=4, pady=2, row=0, column=4, sticky='S' + 'N' + 'E' + 'W')
   Entry(body, textvariable=addr, width=10).grid(padx=4, pady=2, row=0, column=5, sticky='S' + 'N' + 'E' + 'W')

   info = Label(body)
   info.grid(padx=4, pady=2, row=1, column=0, columnspan=5, sticky='S' + 'N' + 'E' + 'W')

   flashButton = Button(body, text='烧录', width=9, command=lambda: StartFlash(info))
   flashButton.grid(row=1, column=5, columnspan=1)

   body.grid(padx=2, pady=2)

   root.mainloop()
