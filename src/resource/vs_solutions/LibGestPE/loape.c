/*****************************************************************************/

#include "stdio.h"
#include "memory.h"
#include "basedef.h"
#include "errors.h"
#include "cpudef.h"
#include "loape.h"

/*****************************************************************************/

t_uint32 VerifImgPe (t_uint8* pImg, t_uint32 dimImg, t_des_zone_pe* pDesZone,
                           t_uint32* pCodErr)
{
  t_int32 esito;                    /* Esito (valore di ritorno) */
  t_uint32 flagErr;                 /* Indicatore di errore */
  t_uint32 offset;                  /* Offset corrente nell'immagine */
  t_image_data_directory* pDataDir; /* Puntatore a 'image data directory' nell'immagine */

  /* Inizializzazione variabili locali */
  esito = 0;
  flagErr = 0;
  offset = 0;
  pDataDir = NULL;

  /* Verifica parametri di input */
  if ((NULL == pImg) || (NULL == pDesZone)) {
    flagErr = 1;
    if (NULL != pCodErr) *pCodErr = EGPE_BADPARAM;
  }

  if (0 == flagErr) {
    /* Inizializzazione descrittore zone immagine PE */
    pDesZone->pDosHeader = NULL;
    pDesZone->pPeSignature = NULL;
    pDesZone->pCoffHeader = NULL;
    pDesZone->pOptionalHeaderStandard = NULL;
    pDesZone->pOptionalHeaderWindows = NULL;
    pDesZone->vetSectHeader = NULL;
    pDesZone->numSect = 0;
    /* Verifica dimensione immagine sufficiente per intestazione DOS */
    if (dimImg >= sizeof(t_dos_header)) {
      /* Puntatore a intestazione DOS */
      pDesZone->pDosHeader = (t_dos_header*) pImg;
      /* Verifica DOS signature */
      if (pDesZone->pDosHeader->eMagic != IMAGE_DOS_SIGNATURE) {
        pDesZone->pDosHeader = NULL;
        flagErr = 1;
        if (NULL != pCodErr) *pCodErr = EGPE_DOSSIGNATURE;
      }
    }else {
      flagErr = 1;
      if (NULL != pCodErr) *pCodErr = EGPE_DOSHDBOUND;
    }
  }

  if (0 == flagErr) {
    if (pDesZone->pDosHeader != NULL) {
      /* Verifica dimensione immagine sufficiente per PE signature */
      offset = pDesZone->pDosHeader->offsetPeHeader + sizeof(t_pe_signature);
      if (dimImg >= offset) {
        /* Puntatore a PE signature */
        pDesZone->pPeSignature = (t_pe_signature*)
                                 (pImg + pDesZone->pDosHeader->offsetPeHeader);
        /* Verifica PE signature */
        if (pDesZone->pPeSignature->signature != IMAGE_PE_SIGNATURE) {
          pDesZone->pPeSignature = NULL;
          flagErr = 1;
          if (NULL != pCodErr) *pCodErr = EGPE_PESIGNATURE;
        }
      }else {
        flagErr = 1;
        if (NULL != pCodErr) *pCodErr = EGPE_PEHDBOUND;
      }
    }
  }

  if (0 == flagErr) {
    if (NULL != pDesZone->pPeSignature) {
      /* Verifica dimensione immagine sufficiente per intestazione COFF */
      offset += sizeof(t_coff_header);
      if (dimImg >= offset) {
        /* Puntatore a intestazione COFF */
        pDesZone->pCoffHeader = (t_coff_header*) (pDesZone->pPeSignature + 1);
      } else {
        flagErr = 1;
        if (NULL != pCodErr) *pCodErr = EGPE_COFFHDBOUND;
      }
    }
  }

  if (0 == flagErr) {
    if (NULL != pDesZone->pCoffHeader) {
      /* Verifca dimensione immagine sufficiente per intestazione opzionale standard */
      offset += sizeof(t_optional_header_standard);
      if (dimImg >= offset) {
        /* Puntatore a intestazione opzionale standard  */
        pDesZone->pOptionalHeaderStandard = (t_optional_header_standard*)
                                            (pDesZone->pCoffHeader + 1);
        /* Verifica che l'immagine sia di tipo PE32 */
        if (pDesZone->pOptionalHeaderStandard->magic != IMAGE_MAGIC_PE32) {
          pDesZone->pOptionalHeaderStandard = NULL;
          flagErr = 1;
          if (NULL != pCodErr) *pCodErr = EGPE_NOEXEPE32;
        }
      }else {
        flagErr = 1;
        if (NULL != pCodErr) *pCodErr = EGPE_OHSHDBOUND;
      }
    }
  }

  if (0 == flagErr) {
    if (NULL != pDesZone->pOptionalHeaderStandard) {
      /* Verifca dimensione immagine sufficiente per intestazione opzionale Windows */
      offset += sizeof(t_optional_header_windows);
      if (dimImg >= offset) {
        /* Puntatore a intestazione opzionale Windows  */
        pDesZone->pOptionalHeaderWindows = (t_optional_header_windows*)
                                           (pDesZone->pOptionalHeaderStandard + 1);
      }else {
        flagErr = 1;
        if (NULL != pCodErr) *pCodErr = EGPE_OHWHDBOUND;
      }
    }
  }

  if (0 == flagErr) {
    if (NULL != pDesZone->pOptionalHeaderWindows) {
      /* Numero di sezioni */
      pDesZone->numSect = pDesZone->pCoffHeader->numberOfSections;
      /* Verifca dimensione immagine sufficiente per vettore intestazioni sezioni */
      offset += ((pDesZone->pOptionalHeaderWindows->numberOfRvaAndSizes *
                                            sizeof(t_image_data_directory)) +
                 (pDesZone->numSect * sizeof(t_section_header)));
      if (dimImg >= offset) {
        /* Puntatore a vettore intestazioni sezioni */
        pDesZone->vetSectHeader = (t_section_header*)
                      (((t_uint8*)(pDesZone->pOptionalHeaderWindows + 1)) +
                       (pDesZone->pOptionalHeaderWindows->numberOfRvaAndSizes *
                        sizeof(t_image_data_directory)));
      }else {
        flagErr = 1;
        if (NULL != pCodErr) *pCodErr = EGPE_SECTHDBOUND;
      }
    }
  }

  if (0 == flagErr) {
    if (NULL != pDesZone->vetSectHeader) {
      /* Verifica che non ci sia niente da rilocare */
      if (BASE_RELOC_TABLE_IND < pDesZone->pOptionalHeaderWindows->numberOfRvaAndSizes) {
        pDataDir = (t_image_data_directory*) (pDesZone->pOptionalHeaderWindows + 1);
        pDataDir += BASE_RELOC_TABLE_IND;
        if ((0 != pDataDir->rva) && (0 != pDataDir->size)) {
          flagErr = 1;
          if (NULL != pCodErr) *pCodErr = EGPE_RELOC;
        }
      }
    }
  }

  if (0 == flagErr) {
    /* Esito OK */
    esito = 1;
  }

  return esito;
}

/*****************************************************************************/

t_uint32 GetChecksumPE(t_uint8* pSrcPe, t_uint32 dimSrcPe, t_uint32* pChecksum, t_uint32* pCodErr)
{
  t_uint32 esito; /* Esito (valore di ritorno) */
  t_des_zone_pe desZone; /* Descrittore di zone in immagine PE */

  /* Pulizia del codice di errore */
  if (NULL != pCodErr) *pCodErr = 0;

  /* Verifica parametri */
  if ((NULL == pSrcPe) || (0 == dimSrcPe) || (NULL == pChecksum)) {
    esito = 0;
    if (NULL != pCodErr) *pCodErr = 1;
  
  } else {

    *pChecksum = 0;

    /* Verifica che l'immagine sia un eseguibile PE e individuazione zone */
    if (0 == VerifImgPe (pSrcPe, dimSrcPe, &desZone, pCodErr)) {
      esito = 0;
  
    } else {
      /* Checksum recuperato */
      *pChecksum = desZone.pOptionalHeaderWindows->checkSum;
      /* Esito corretto */
      esito = 1;
    }
  }

  return esito;
}

t_uint32 GetTextAreaPE(t_uint8* pSrcPe, t_uint32 dimSrcPe, t_uint32** ppText, t_uint32* pTextSize, t_uint32* pCodErr)
{
	t_uint32 esito; /* Esito (valore di ritorno) */
	t_des_zone_pe desZone; /* Descrittore di zone in immagine PE */
	t_section_header* sect;
	t_uint32 i;
	t_uint32 numSect;
	t_uint8 found;

	esito = 0;

	/* Pulizia del codice di errore */
	if (NULL != pCodErr) *pCodErr = 0;
	if (NULL != ppText) *ppText = NULL;
	if (NULL != pTextSize) *pTextSize = 0;

	/* Verifica parametri */
	if ((NULL == pSrcPe) || (0 == dimSrcPe)) {
		esito = 0;
		if (NULL != pCodErr) *pCodErr = 1;

	}
	else {

		/* Verifica che l'immagine sia un eseguibile PE e individuazione zone */
		if (0 == VerifImgPe(pSrcPe, dimSrcPe, &desZone, pCodErr)) {
			esito = 0;
		}
		else {
			// Vai area .text
			sect = NULL;
			i = 0;
			numSect = desZone.numSect;
			found = 0;
			while (i < numSect && !found) {
				sect = &desZone.vetSectHeader[i];

				if (memcmp(sect->name, ".text", 5) == 0) {
					**ppText = sect->pointerToRawData;
					*pTextSize = sect->sizeOfRawData;
					
					found = 1;
					esito = 1;
				}
				i++;
			}
		}
	}

	return esito;
}


/*****************************************************************************/

t_uint32 SetChecksumPE (t_uint8* pSrcPe, t_uint32 dimSrcPe, t_uint32 iChecksum, t_uint32* pCodErr)
{
  t_uint32 esito; /* Esito (valore di ritorno) */
  t_des_zone_pe desZone; /* Descrittore di zone in immagine PE */

  esito = 0;

  /* Pulizia del codice di errore */
  if (NULL != pCodErr) *pCodErr = 0;

  /* Verifica parametri */
  if ((NULL == pSrcPe) || (0 == dimSrcPe)) {
    esito = 0;
    if (NULL != pCodErr) *pCodErr = 1;
  
  } else {

    /* Verifica che l'immagine sia un eseguibile PE e individuazione zone */
    if (0 == VerifImgPe (pSrcPe, dimSrcPe, &desZone, pCodErr)) {
      esito = 0;
  
    } else {
      /* Impostazione del checksum */
      desZone.pOptionalHeaderWindows->checkSum = iChecksum;
      /* Esito corretto */
      esito = 1;
    }
  }

  return esito;
}

/*****************************************************************************/

t_uint32 GetTimeDateStampPE(t_uint8 *pSrcPe, t_uint32 dimSrcPe, t_uint32 *pTimeDateStamp, t_uint32* pCodErr)
{
  t_uint32 esito; /* Esito (valore di ritorno) */
  t_des_zone_pe desZone; /* Descrittore di zone in immagine PE */

  /* Pulizia del codice di errore */
  if (NULL != pCodErr) *pCodErr = 0;

  /* Verifica parametri */
  if ((NULL == pSrcPe) || (0 == dimSrcPe) || (NULL == pTimeDateStamp)) {
    esito = 0;
    if (NULL != pCodErr) *pCodErr = 1;
  
  } else {

    /* Verifica che l'immagine sia un eseguibile PE e individuazione zone */
    if (0 == VerifImgPe (pSrcPe, dimSrcPe, &desZone, pCodErr)) {
      esito = 0;
  
    } else {
      /* Time Date Stamp */
      *pTimeDateStamp = desZone.pCoffHeader->timeDateStamp;
      /* Esito corretto */
      esito = 1;
    }
  }

  return esito;
}

/*****************************************************************************/

t_uint32 SetTimeDateStampPE(t_uint8 *pSrcPe, t_uint32 dimSrcPe, t_uint32 iTimeDateStamp, t_uint32* pCodErr)
{
  t_uint32 esito; /* Esito (valore di ritorno) */
  t_des_zone_pe desZone; /* Descrittore di zone in immagine PE */

  /* Pulizia del codice di errore */
  if (NULL != pCodErr) *pCodErr = 0;

  /* Verifica parametri */
  if ((NULL == pSrcPe) || (0 == dimSrcPe)) {
    esito = 0;
    if (NULL != pCodErr) *pCodErr = 1;
  
  } else {

    /* Verifica che l'immagine sia un eseguibile PE e individuazione zone */
    if (0 == VerifImgPe (pSrcPe, dimSrcPe, &desZone, pCodErr)) {
      esito = 0;
  
    } else {
      /* Time Date Stamp */
      desZone.pCoffHeader->timeDateStamp = iTimeDateStamp;
      /* Esito corretto */
      esito = 1;
    }
  }

  return esito;
}

/*****************************************************************************/

t_uint32 CutRichSignaturePE(t_uint8* pSrcPe, t_uint32* pDimSrcPe, t_uint32* pCodErr)
{
  t_uint32 esito = 0;
  t_des_zone_pe desZone; /* Descrittore di zone in immagine PE */
  t_uint32 offsetPeHeader = 0; /* Offset nel file dell'header PE */
  t_uint32 iRichSignSize = 0; /* Dimensione della Rich Signature */
  t_uint32 iFirstSect = 0; /* Indice nel file della prima sezione */
  t_uint32 i = 0;
  t_uint32 origChk = 0;
  t_uint32 calcChk = 0;

  if (NULL != pCodErr) *pCodErr = 0;
  
  
  /* Verifica parametri */
  if ((NULL == pSrcPe) || (0 == *pDimSrcPe)) {
    esito = 0;
    if (NULL != pCodErr) *pCodErr = 1;
  } else {
  
    /* Verifica che l'immagine sia un eseguibile PE e individuazione zone */
    if (0 == VerifImgPe (pSrcPe, *pDimSrcPe, &desZone, pCodErr)) {
      esito = 0;
      if (NULL != pCodErr) *pCodErr = 2;
    } else {
  
      /* Offset dell'header PE */
      offsetPeHeader = desZone.pDosHeader->offsetPeHeader;  
      /* Dimensione della Rich Signature */
      iRichSignSize = offsetPeHeader - 0x80;
  
      if (0 == iRichSignSize) {
        esito = 1;
      } else {
        /*
         * Esiste la Rich Signature, occorre eliminarla spostando gli header seguenti.
         * La Rich Signature da eliminare ha dimensioni variabili, ma parte sempre dal byte
         * 0x80 e finisce subito prima dell'header PE.
         * Occorre però spostare i soli header, lasciando ferme le sezioni di codice
         * e dati: per farlo si aggiunge un padding di n zeri prima della prima sezione,
         * con n uguale alla dimensione della rich signature cancellata. 
         */

        /* Correzione dell'offset dell'header PE nel file, prima di modificare il file */
        desZone.pDosHeader->offsetPeHeader = 0x80;
        
        /* indice della prima sezione (prima della quale aggiungere il padding di 0) */
        iFirstSect = desZone.vetSectHeader->pointerToRawData;

        for (i = offsetPeHeader; i < iFirstSect; i++) {
          pSrcPe[i - iRichSignSize] = pSrcPe[i];
        }

        for (i = iFirstSect - iRichSignSize; i < iFirstSect; i++) {
          pSrcPe[i] = 0;
        }

        /* Occorre ricalcolare gli indici delle zone! */
        if (1 != VerifImgPe (pSrcPe, *pDimSrcPe, &desZone, pCodErr)) {
          esito = 0;
          if (NULL != pCodErr) *pCodErr = 3;
        } else {

          /* Correzione del checksum PE */
          PeVerifChecksum (pSrcPe, *pDimSrcPe, &origChk, &calcChk, pCodErr);
          desZone.pOptionalHeaderWindows->checkSum = calcChk;

          if (1 != PeVerifChecksum (pSrcPe, *pDimSrcPe, &origChk, &calcChk, pCodErr)) {
            esito = 0;
            if (NULL != pCodErr) *pCodErr = 4;
          } else {
            esito = 1;
          }
        }
      }
    }
  }
  return esito;
}

/*****************************************************************************/

t_uint32 PeVerifChecksum (t_uint8* pSrcPe, t_uint32 dimSrcPe, t_uint32* pOrigChk,
                         t_uint32* pCalcChk, t_uint32* pCodErr)
{
  t_uint32 esito;            /* Esito (valore di ritorno) */
  t_des_zone_pe desZone;    /* Descrittore di zone in immagine PE */
  t_uint32 origChecksun;    /* Checksum originale */
  t_uint32 checksum;        /* Checksum calcolato */
  t_uint16* pCor;           /* Puntatore corrente in immagine */
  t_uint16* pLim;           /* Puntatore limite in immagine */

  /* Inizializzazione esito (come errore) */
  esito = 0;

  /* Verifica parametri */
  if ((NULL != pSrcPe) && (0 < dimSrcPe)) {

    /* Verifica che l'immagine sia un eseguibile PE e individuazione zone */
    if (VerifImgPe (pSrcPe, dimSrcPe, &desZone, pCodErr) != 0) {

      /* Salvataggio checksum originale e suo temporaneo azzeramento nell'immagine */
      origChecksun = desZone.pOptionalHeaderWindows->checkSum;
      desZone.pOptionalHeaderWindows->checkSum = 0;

      /* Calcolo del checksum */
      checksum = 0;
      pCor = (t_uint16*) pSrcPe;
      pLim = pCor + (dimSrcPe / 2);
      while (pCor < pLim) {
        checksum += *pCor++;
        checksum = 0xFFFF & (checksum + (checksum >> 16));
      }
      if ((dimSrcPe & 1) != 0) {
        checksum += *((t_uint8*)pCor);
        checksum =  0xFFFF & (checksum + (checksum >> 16));
      }
      checksum += dimSrcPe;

      /* Ripristino checksum originale */
      desZone.pOptionalHeaderWindows->checkSum = origChecksun;

      /* Memorizzazione checksum originale e calcolato, se richiesti */
      if (pOrigChk != NULL) *pOrigChk = origChecksun;
      if (pCalcChk != NULL) *pCalcChk = checksum;

      /* Verifica checksum */
      if (checksum == origChecksun) {
        /* Esito OK */
        esito = 1;
      }

    } /* Fine verifica che l'immagine sia un eseguibile PE */

  } /* Fine verifica parametri */

   return esito;
}

