#include "dmm_flow.h"

void task_dmm() {
	dmm(filter->data, src->data, dest->data, rows, cols, dcols);
	cwait();
}