import pylink
jlink_dll_path = './JLink_x64.dll'
jlink = pylink.JLink(lib=pylink.library.Library(dllpath=jlink_dll_path))

print(jlink.connected_emulators(host=pylink.enums.JLinkHost.USB))

# jlink.open("25952325")
# jlink.set_tif(pylink.enums.JLinkInterfaces.SWD)
#
# jlink.connect('N32G031C8',speed=8000, verbose=True)
#
# print('ARM Id: %d' % jlink.core_id())
# print('CPU Id: %d' % jlink.core_cpu())
# print('Core Name: %s' % jlink.core_name())
# print('Device Family: %d' % jlink.device_family())
#
# jlink.erase()
#
# jlink.flash_file(r'D:/Coding/embed_process/Program/Program/Objects/TemperatureAcquisition.hex', 0x8000000)
#
# jlink.reset()
# jlink.close()
