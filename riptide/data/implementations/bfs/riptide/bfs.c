#include "stdint.h"

#include "helpers.h"

#undef PTR
#define PTR(typ) typ *

void bfs(CONST_PTR(uint16_t) rows, CONST_PTR(uint16_t) cols, uint16_t count, 
	PTR(uint16_t) queue, PTR(uint16_t) visited, PTR(uint16_t) walk) {
 
	uint32_t queue_front = 0;
	uint32_t queue_back = 1;
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

	// Walk in BFS order
	while(!empty()) {

		// Fetch the next vertex and add it to @walk
		uint16_t next = pop();
		walk[walk_pos] = next;
		walk_pos++;

		// Add unvisited neighbors to the queue
		for(uint32_t i = rows[next] ; i < rows[next + 1]; i++) {
			uint32_t dst = cols[i];
			if(!visited[dst]) {
				push(dst);
				visited[dst] = 1;
			}
		}
	}
}