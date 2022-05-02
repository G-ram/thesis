#include "smv_flow.h"

void task_smv() {
	smv(filter->sparse.sizes, filter->sparse.offsets, 
		filter->data, src->data, dest->data, rows);
	cwait();
}