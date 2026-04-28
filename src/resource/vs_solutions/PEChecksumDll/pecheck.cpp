//#include "windows.h"
#include "basedef.h"
//#include "syscall.h"
//#include "checksum.h"
#include "cpudef.h"
//#include "comkrn.h"
#include "loape.h"
#include "pecheck.h"



API_DLL t_uint32 get_checksum(t_uint8* pSrcPe, t_uint32 dimSrcPe, t_uint32* pChecksum, t_uint32* pCodErr)
{
	t_uint32 res = GetChecksumPE(pSrcPe, dimSrcPe, pChecksum, pCodErr);

	return res;
}

API_DLL t_uint32 set_checksum(t_uint8* pSrcPe, t_uint32 dimSrcPe, t_uint32 iChecksum, t_uint32* pCodErr)
{
	t_uint32 res = SetChecksumPE(pSrcPe, dimSrcPe, iChecksum, pCodErr);

	return res;
}

API_DLL t_uint32 get_timestamp(t_uint8 *pSrcPe, t_uint32 dimSrcPe, t_uint32 *pTimeDateStamp, t_uint32* pCodErr)
{
	t_uint32 res = GetTimeDateStampPE(pSrcPe, dimSrcPe, pTimeDateStamp, pCodErr);

	return res;
}

API_DLL t_uint32 set_timestamp(t_uint8 *pSrcPe, t_uint32 dimSrcPe, t_uint32 iTimeDateStamp, t_uint32* pCodErr)
{
	t_uint32 res = SetTimeDateStampPE(pSrcPe, dimSrcPe, iTimeDateStamp, pCodErr);

	return res;
}

API_DLL t_uint32 verify_checksum(t_uint8* pSrcPe, t_uint32 dimSrcPe, t_uint32* pOrigChk, t_uint32* pCalcChk, t_uint32* pCodErr) 
{
	t_uint32 res = PeVerifChecksum(pSrcPe, dimSrcPe, pOrigChk, pCalcChk, pCodErr);

	return res;
}





