#ifndef HELPERS_H_
#define HELPERS_H_

#include "stdint.h"
#include "stdbool.h"

extern int16_t clip(int16_t v, unsigned f);
extern int16_t cgra_load(int16_t * ptr, uint32_t idx, ...);
extern int16_t cgra_store(int16_t * ptr, uint32_t idx, int16_t val_to_store, ...);

#if defined(ALIAS_ANNOTATE)
	#define no_alias __attribute__((annotate("no_alias")))
	#define PTR(typ) typ * no_alias
	#define CONST_PTR(typ) PTR(typ)
#elif defined(ALIAS_RESTRICT)
	#define CONST_PTR(typ) const typ * restrict
	#define PTR(typ) typ * restrict
#else
	#define PTR(typ) typ *
	#define CONST_PTR(typ) PTR(typ)
#endif

#endif
