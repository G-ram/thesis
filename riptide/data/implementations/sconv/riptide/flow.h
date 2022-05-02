#include "sconv_flow.h"

uint16_t Brow[TILE_SIZE * TILE_SIZE];
uint16_t Bcol[TILE_SIZE * TILE_SIZE];

void task_sconv() {
	uint32_t scols = cols + fcols - 1;
	uint32_t idx = 0;

	for(uint32_t i = 0; i < total_elements; i++) {
		idx += filter->sparse.offsets[i];
		Brow[i] = idx / fcols; 
		Bcol[i] = idx % fcols;
	}

	sconv(src->data, Brow, Bcol, filter->data,
		dest->data, rows, cols, scols, total_elements - 1);
	cwait();	
}
