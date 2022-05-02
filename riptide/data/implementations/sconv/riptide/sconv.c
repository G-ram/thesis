#include "stdint.h"

#include "helpers.h"

void sconv(CONST_PTR(int16_t) A, CONST_PTR(uint16_t) Brow, 
	CONST_PTR(uint16_t) Bcol, CONST_PTR(int16_t) B, PTR(int16_t) Z, 
	uint32_t rowBound, uint32_t colBound, uint32_t n, uint32_t total_elements) {

	uint32_t row = 0;
	for(uint32_t i = 0; i < rowBound; i++) {
		uint32_t offset = i * n;
		for(uint32_t j = 0; j < colBound; j++) {

			int16_t w = 0;
			for(uint32_t k = 0; k < total_elements; k++) {
				uint32_t frow = Brow[k];
				uint32_t fcol = Bcol[k];
				 w += clip(B[k] * A[offset + frow * n + fcol], 5);
			}

			Z[row + j] = w;
			offset++;
		}
		row += colBound;
	}
}
