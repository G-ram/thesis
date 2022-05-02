#include "bfs_panic.h"

void task_bfs() {
	uint16_t len = 0;

	uint32_t queue_front = 0;
	uint32_t queue_back = 0;
	uint32_t walk_pos = 0;

	// Generic helpers for @queue
	#define push(val) \
	({ \
		queue[queue_back] = val; \
		queue_back++; \
	})

	#define pop() \
	({ \
		uint16_t val = queue[queue_front]; \
		queue_front++; \
		val; \
	})

	#define empty() (queue_front == queue_back)

	// Begin the BFS w/ @start, mark visited
	push(start);
	visited[start] = 1;

	while(!empty()) {

		// Fetch the next vertex and add it to @walk
		uint16_t next = pop();
		walk[walk_pos] = next;
		walk_pos++;

		// Add unvisited neighbors to the queue
		uint16_t tmp;
		uint32_t start = rows[next];
		uint32_t stop = rows[next + 1];
		int32_t diff = stop - start;
		if(diff <= 0) continue;
		vcfg(diff, _kernel);
		vtfr(cols + start, BFS_PANIC_VTFR0);
		vtfr(visited, BFS_PANIC_VTFR1);
		vtfr(visited, BFS_PANIC_VTFR2);
		vtfr(queue + queue_back - 1, BFS_PANIC_VTFR3);
		vtfr(&tmp - diff + 1, BFS_PANIC_VTFR4);
		vfence();
		queue_back += tmp;
	}

}