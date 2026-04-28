

#ifndef API_DLL
#define API_DLL __declspec(dllexport)
#endif

extern "C" API_DLL t_uint32 get_checksum(t_uint8* pSrcPe, t_uint32 dimSrcPe, t_uint32* pChecksum, t_uint32* pCodErr);
extern "C" API_DLL t_uint32 set_checksum(t_uint8* pSrcPe, t_uint32 dimSrcPe, t_uint32 iChecksum, t_uint32* pCodErr);
extern "C" API_DLL t_uint32 get_timestamp(t_uint8 *pSrcPe, t_uint32 dimSrcPe, t_uint32 *pTimeDateStamp, t_uint32* pCodErr);
extern "C" API_DLL t_uint32 set_timestamp(t_uint8 *pSrcPe, t_uint32 dimSrcPe, t_uint32 iTimeDateStamp, t_uint32* pCodErr);
extern "C" API_DLL t_uint32 verify_checksum(t_uint8* pSrcPe, t_uint32 dimSrcPe, t_uint32* pOrigChk, t_uint32* pCalcChk, t_uint32* pCodErr);
