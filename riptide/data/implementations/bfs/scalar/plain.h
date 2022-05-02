void task_bfs() {

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

	// Walk in BFS order
	while(!empty()) {

		// Fetch the next vertex and add it to @walk
		uint16_t next = pop();
		walk[walk_pos] = next;
		walk_pos++;

		// Add unvisited neighbors to the queue
		for(uint16_t i = rows[next]; i < rows[next + 1]; i++) {
			uint32_t dst = cols[i];
			if(!visited[dst]) {
				push(dst);
				visited[dst] = 1;
			}
		}
	}
}