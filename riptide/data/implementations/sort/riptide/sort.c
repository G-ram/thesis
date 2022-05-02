#include "stdint.h"

#include "helpers.h"

void sort(PTR(int16_t) A, PTR(int16_t) Z, uint32_t size, uint32_t even_count) {
	uint32_t count = even_count;
	for(uint16_t i = 0; i < 16; i++) {
		
		uint16_t odd = i & 0x1;
		PTR(int16_t) src = (odd) ? Z : A; 
		PTR(int16_t) dst = (odd) ? A : Z;

		uint32_t idx0 = 0;
		uint32_t idx1 = count;
		uint32_t next_count = 0;
		for(uint32_t j = 0; j < size; j++) {
			int16_t v = src[j];
			int16_t o = (v >> i) & 0x1;
			next_count += (v & (1 << (i + 1))) == 0x0;
			
			if(o) dst[idx1++] = v;
			else dst[idx0++] = v;
		}

    	count = next_count;
	}
}
