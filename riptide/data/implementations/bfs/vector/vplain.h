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
		uint16_t stop = rows[next + 1];
		for(uint16_t i = rows[next]; i < stop; i += len) {
			vsetvl(len, stop - i);
			vlh(v1, cols + i);
			vlxh(v2, visited, v1);
			vseqi(v0, v2, 0);
			vsxh(visited, v0.m, v1);
			vpresum(v4, v0);
			vsxh(queue + queue_back - 1, v1.m, v4);
			vredsum(v4, v0);

			uint16_t tmp;
			vsetvl(tmp, 1);
			vsh(&tmp, v4);
			vfence();
			queue_back += tmp;
		}
	}

}
