#include "stdint.h"

#include "helpers.h"

void smv(CONST_PTR(uint16_t) Arow, CONST_PTR(uint16_t) Acol, 
	CONST_PTR(int16_t) A, CONST_PTR(int16_t) B, PTR(int16_t)Z, uint32_t m) {
	for(uint32_t i = 0; i < m; i++) {
		uint32_t start = Arow[i];
		uint32_t end = Arow[i + 1];
		int16_t w = 0;
		for(uint32_t j = start; j < end; j++) {
			w += clip(A[j] * B[Acol[j]], 5);
		}
		Z[i] = w;
	}
}
