#include "stdint.h"

#include "helpers.h"

void dconv(CONST_PTR(int16_t) A, PTR(int16_t) B, PTR(int16_t) Z, 
	uint32_t size, uint32_t cols, uint32_t scols, 
	uint32_t frows, uint32_t fcols) {

	uint32_t row = 0;
	uint32_t col = 0;
	for(uint32_t i = 0; i < size; i++) {
		int16_t w = 0;
		uint32_t offset = row * scols + col;

		for(uint32_t j = 0; j < frows; j++) {
			for(uint32_t k = 0; k < fcols; k++) {
				w += clip(A[offset + scols * j + k] * B[j * frows + k], 5);
			}
		}
		Z[i] = w;

		col++;
		if(col == cols) {
			row++;
			col = 0;
		}
	}
}
