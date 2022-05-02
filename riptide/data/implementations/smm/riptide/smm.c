#include "stdint.h"

#include "helpers.h"

void smm(CONST_PTR(uint16_t) Arow, CONST_PTR(uint16_t) Acol, 
	CONST_PTR(int16_t) A, CONST_PTR(uint16_t) Brow, CONST_PTR(uint16_t) Bcol, 
	CONST_PTR(int16_t) B, PTR(int16_t) Z, uint32_t rows, uint32_t cols) {

	int16_t *dest_ptr = Z; 
	for(uint32_t i = 0; i < rows; i++) {
		uint32_t j_start = Arow[i];
		uint32_t j_end = Arow[i + 1];
		for(uint32_t j = j_start; j < j_end; j++) {
			uint32_t row = Acol[j];	
			uint32_t k_start = Brow[row];
			uint32_t k_end = Brow[row + 1];
			int16_t f = A[j];
			for(uint32_t k = k_start; k < k_end; k++) {
				int16_t w = clip(f * B[k], 5);
				int16_t *d = dest_ptr + Bcol[k];
				*d += w;
			}
		}
		dest_ptr += cols;
	}
}