from comtypes import *
import comtypes.client
from ctypes import POINTER
from ctypes.wintypes import DWORD, BOOL

#SET SYSTEM VOLUME
########################################################################
"""
Set the system volume to the level given
Parameters:
    level: (int from 0 --> 100) the desired volume level
"""
########################################################################
def set_volume(level):
    level = int(level)
    dec = decibels()
    endpoint = enumerator.GetDefaultAudioEndpoint(0, 1)
    volume = endpoint.Activate(IID_IAudioEndpointVolume,
                               comtypes.CLSCTX_INPROC_SERVER, None )
    volume.SetMasterVolumeLevel(dec[level], None)

#GET SYSTEM VOLUME
########################################################################
"""
Get the current system volume level
Return Value:
	(int from 0 --> 100) The level of system volume 
"""
########################################################################
def get_volume():
    endpoint = enumerator.GetDefaultAudioEndpoint( 0, 1 )
    volume = endpoint.Activate(IID_IAudioEndpointVolume,
                                comtypes.CLSCTX_INPROC_SERVER, None)
    dec = decibels()
    vol = volume.GetMasterVolumeLevel()
    val = -1
    for i in range(len(dec)):
        if abs(dec[i] - vol) < .0001:
            val = i
    return val

def decibels():
    return [-64, -56.260887146, -51.1573905945, 
            -47.3434371948, -44.2970657349, 
            -41.7604827881, -39.5872802734, 
            -37.6862716675, -35.996799469, 
            -34.4764671326, -33.0944633484, 
            -31.8277072906, -30.6584472656, 
            -29.5727405548, -28.5594387054, 
            -27.6094856262, -26.7154273987, 
            -25.8710441589, -25.0711097717, 
            -24.3111782074, -23.5874347687, 
            -22.8965930939, -22.2357883453, 
            -21.6025161743, -20.9945774078, 
            -20.4100208282, -19.847114563, 
            -19.3043117523, -18.7802257538, 
            -18.2736091614, -17.7833328247, 
            -17.308380127, -16.8478183746, 
            -16.400800705, -15.9665555954, 
            -15.5443716049, -15.133597374, 
            -14.7336330414, -14.3439245224, 
            -13.9639577866, -13.5932559967, 
            -13.23138237, -12.8779230118, 
            -12.5324954987, -12.1947450638, 
            -11.8643360138, -11.5409564972, 
            -11.224313736, -10.9141330719, 
            -10.6101551056, -10.3121376038, 
            -10.0198507309, -9.7330780029, 
            -9.4516162872, -9.1752700806, 
            -8.9038600922, -8.6372108459, 
            -8.3751592636, -8.1175479889, 
            -7.8642311096, -7.615064621, 
            -7.3699183464, -7.128663063, 
            -6.8911771774, -6.6573448181, 
            -6.427054882, -6.2002010345, 
            -5.9766840935, -5.7564063072, 
            -5.5392751694, -5.3252019882, 
            -5.1141023636, -4.9058923721, 
            -4.7004976273, -4.4978413582, 
            -4.2978510857, -4.1004581451, 
            -3.9055957794, -3.7132000923, 
            -3.5232076645, -3.3355622292, 
            -3.1502046585, -2.9670803547, 
            -2.7861361504, -2.6073203087, 
            -2.4305827618, -2.2558774948, 
            -2.0831575394, -1.9123780727, 
            -1.7434961796, -1.5764698982, 
            -1.4112581015, -1.247823596, 
            -1.086127758, -0.9261339307, 
            -0.76780653, -0.6111113429, 
            -0.4560140669, -0.3024843037, 
            -0.1504897326, 0]

MMDeviceApiLib = \
    GUID('{2FDAAFA3-7523-4F66-9957-9D5E7FE698F6}')
IID_IMMDevice = \
    GUID('{D666063F-1587-4E43-81F1-B948E807363F}')
IID_IMMDeviceEnumerator = \
    GUID('{A95664D2-9614-4F35-A746-DE8DB63617E6}')
CLSID_MMDeviceEnumerator = \
    GUID('{BCDE0395-E52F-467C-8E3D-C4579291692E}')
IID_IMMDeviceCollection = \
    GUID('{0BD7A1BE-7A1A-44DB-8397-CC5392387B5E}')
IID_IAudioEndpointVolume = \
    GUID('{5CDF2C82-841E-4546-9722-0CF74078229A}')

class IMMDeviceCollection(IUnknown):
    _iid_ = GUID('{0BD7A1BE-7A1A-44DB-8397-CC5392387B5E}')
    pass

class IAudioEndpointVolume(IUnknown):
    _iid_ = GUID('{5CDF2C82-841E-4546-9722-0CF74078229A}')
    _methods_ = [
        STDMETHOD(HRESULT, 'RegisterControlChangeNotify', []),
        STDMETHOD(HRESULT, 'UnregisterControlChangeNotify', []),
        STDMETHOD(HRESULT, 'GetChannelCount', []),
        COMMETHOD([], HRESULT, 'SetMasterVolumeLevel',
            (['in'], c_float, 'fLevelDB'),
            (['in'], POINTER(GUID), 'pguidEventContext')
        ),
        COMMETHOD([], HRESULT, 'SetMasterVolumeLevelScalar',
            (['in'], c_float, 'fLevelDB'),
            (['in'], POINTER(GUID), 'pguidEventContext')
        ),
        COMMETHOD([], HRESULT, 'GetMasterVolumeLevel',
            (['out','retval'], POINTER(c_float), 'pfLevelDB')
        ),
        COMMETHOD([], HRESULT, 'GetMasterVolumeLevelScalar',
            (['out','retval'], POINTER(c_float), 'pfLevelDB')
        ),
        COMMETHOD([], HRESULT, 'SetChannelVolumeLevel',
            (['in'], DWORD, 'nChannel'),
            (['in'], c_float, 'fLevelDB'),
            (['in'], POINTER(GUID), 'pguidEventContext')
        ),
        COMMETHOD([], HRESULT, 'SetChannelVolumeLevelScalar',
            (['in'], DWORD, 'nChannel'),
            (['in'], c_float, 'fLevelDB'),
            (['in'], POINTER(GUID), 'pguidEventContext')
        ),
        COMMETHOD([], HRESULT, 'GetChannelVolumeLevel',
            (['in'], DWORD, 'nChannel'),
            (['out','retval'], POINTER(c_float), 'pfLevelDB')
        ),
        COMMETHOD([], HRESULT, 'GetChannelVolumeLevelScalar',
            (['in'], DWORD, 'nChannel'),
            (['out','retval'], POINTER(c_float), 'pfLevelDB')
        ),
        COMMETHOD([], HRESULT, 'SetMute',
            (['in'], BOOL, 'bMute'),
            (['in'], POINTER(GUID), 'pguidEventContext')
        ),
        COMMETHOD([], HRESULT, 'GetMute',
            (['out','retval'], POINTER(BOOL), 'pbMute')
        ),
        COMMETHOD([], HRESULT, 'GetVolumeStepInfo',
            (['out','retval'], POINTER(c_float), 'pnStep'),
            (['out','retval'], POINTER(c_float), 'pnStepCount'),
        ),
        COMMETHOD([], HRESULT, 'VolumeStepUp',
            (['in'], POINTER(GUID), 'pguidEventContext')
        ),
        COMMETHOD([], HRESULT, 'VolumeStepDown',
            (['in'], POINTER(GUID), 'pguidEventContext')
        ),
        COMMETHOD([], HRESULT, 'QueryHardwareSupport',
            (['out','retval'], POINTER(DWORD), 'pdwHardwareSupportMask')
        ),
        COMMETHOD([], HRESULT, 'GetVolumeRange',
            (['out','retval'], POINTER(c_float), 'pfMin'),
            (['out','retval'], POINTER(c_float), 'pfMax'),
            (['out','retval'], POINTER(c_float), 'pfIncr')
        ),

    ]

class IMMDevice(IUnknown):
    _iid_ = GUID('{D666063F-1587-4E43-81F1-B948E807363F}')
    _methods_ = [
        COMMETHOD([], HRESULT, 'Activate',
            (['in'], POINTER(GUID), 'iid'),
            (['in'], DWORD, 'dwClsCtx'),
            (['in'], POINTER(DWORD), 'pActivationParans'),
            (['out','retval'], POINTER(POINTER(IAudioEndpointVolume)),
             'ppInterface')
        ),
        STDMETHOD(HRESULT, 'OpenPropertyStore', []),
        STDMETHOD(HRESULT, 'GetId', []),
        STDMETHOD(HRESULT, 'GetState', [])
    ]
    pass

class IMMDeviceEnumerator(comtypes.IUnknown):
    _iid_ = GUID('{A95664D2-9614-4F35-A746-DE8DB63617E6}')

    _methods_ = [
        COMMETHOD([], HRESULT, 'EnumAudioEndpoints',
            (['in'], DWORD, 'dataFlow'),
            (['in'], DWORD, 'dwStateMask'),
            (['out','retval'], POINTER(POINTER(IMMDeviceCollection)),
             'ppDevices')
        ),
        COMMETHOD([], HRESULT, 'GetDefaultAudioEndpoint',
            (['in'], DWORD, 'dataFlow'),
            (['in'], DWORD, 'role'),
            (['out','retval'], POINTER(POINTER(IMMDevice)), 'ppDevices')
        )
    ]





enumerator = comtypes.CoCreateInstance( 
    CLSID_MMDeviceEnumerator,
    IMMDeviceEnumerator,
    comtypes.CLSCTX_INPROC_SERVER
)
