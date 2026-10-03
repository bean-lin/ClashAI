/* Included textually into live_sampler2.c by build_source.py; no game calls. */
enum { EXT_PROJECTILE_VT = 0x19f7370, EXT_AREA_VT = 0x19f6a28 };
static int extended = 0;
typedef struct {
  uint64_t address, vtable_rva, source, target, attached_owner, data_ptr;
  int32_t generation_key, side, x, y, card_id, target_x, target_y;
  int32_t timer_ms_raw, life_override_ms_raw, level;
  int64_t remaining_ms;
} ExtraObject;
typedef struct {
  ExtraObject projectiles[MAX_ENTITIES], effects[MAX_ENTITIES];
  int projectile_count, effect_count, unknown_nonunits, read_errors;
} ExtraFrame;
static ExtraFrame extra;

static int32_t ext_i32(const uint8_t *b, size_t o) {
  int32_t v; memcpy(&v, b + o, 4); return v;
}
static uint64_t ext_u64(const uint8_t *b, size_t o) {
  uint64_t v; memcpy(&v, b + o, 8); return v;
}
static int ext_evo(int32_t card_id) {
  /* This live build uses table 13 form IDs; v1 discarded those bodies.
     A deck evolution eligibility flag is NOT a spawned-body evolution flag. */
  return card_id >= 13000000 && card_id < 14000000;
}
static void read_extended_objects(int fd, uint64_t libg, ChainFrame *frame) {
  uint64_t addresses[MAX_ENTITIES];
  memset(&extra, 0, sizeof(extra));
  if (frame->native_count < 0 || frame->native_count > MAX_ENTITIES ||
      (frame->native_count && (!frame->data ||
       !read_exact(fd, frame->data, addresses, (size_t)frame->native_count * 8)))) {
    extra.read_errors++; return;
  }
  for (int j = 0; j < frame->native_count; ++j) {
    uint8_t raw[0x128];
    if (!addresses[j] || !read_exact(fd, addresses[j], raw, sizeof raw)) {
      extra.read_errors++; continue;
    }
    uint64_t vt = ext_u64(raw, 0);
    uint64_t rva = vt >= libg ? vt - libg : UINT64_MAX;
    int32_t category = ext_i32(raw, 8), side = ext_i32(raw, 0x78);
    int32_t card = ext_i32(raw, 0xac), x = ext_i32(raw, 0x7c), y = ext_i32(raw, 0x80);
    if (category >= 5000000 && category < 6000000 && ext_evo(card)) {
      EntityFrame e = {.address = addresses[j], .category = category,
        .kind = ext_i32(raw, 0x30), .side = side, .x = x, .y = y,
        .card_id = card, .level = ext_i32(raw, 0x120),
        .behavior = ext_i32(raw, 0x11c), .hp = -1, .max_hp = -1};
      if (e.kind < 10 || e.kind > 20 || side < 0 || side > 1 ||
          x < 0 || x > 18000 || y < 0 || y > 32000 ||
          e.level < 0 || e.level > 16 || frame->entity_count >= MAX_ENTITIES) continue;
      uint64_t components = ext_u64(raw, 0x18), hp = 0;
      int32_t pair[2];
      if (components && read_exact(fd, components + 0x10, &hp, 8) && hp &&
          read_exact(fd, hp + 0x10, pair, sizeof pair) && pair[0] >= 0 &&
          pair[1] >= pair[0] && pair[1] <= 100000) {
        e.hp = pair[0]; e.max_hp = pair[1];
      }
      e.level++;
      /* Guard against a second registry read seeing a reused address or duplicate. */
      int duplicate = 0;
      for (int k = 0; k < frame->entity_count; ++k)
        if (frame->entities[k].address == e.address) { duplicate = 1; break; }
      if (!duplicate) {
        frame->entities[frame->entity_count++] = e;
        if (frame->filtered_count > 0) frame->filtered_count--;
      }
      continue;
    }
    if (category < 3000000 || category >= 5000000) continue;
    int projectile = rva == EXT_PROJECTILE_VT && category >= 4000000;
    int effect = rva == EXT_AREA_VT && category < 4000000;
    if ((!projectile && !effect) || side < 0 || side > 1) {
      extra.unknown_nonunits++; continue;
    }
    ExtraObject o = {.address = addresses[j], .vtable_rva = rva,
      .generation_key = category, .side = side, .x = x, .y = y, .card_id = card,
      .data_ptr = ext_u64(raw, 0x48), .remaining_ms = -1};
    if (projectile) {
      o.source = ext_u64(raw, 0x100); o.target = ext_u64(raw, 0x108);
      o.attached_owner = ext_u64(raw, 0x118);
      o.target_x = ext_i32(raw, 0x120); o.target_y = ext_i32(raw, 0x124);
      if (extra.projectile_count < MAX_ENTITIES)
        extra.projectiles[extra.projectile_count++] = o;
    } else {
      o.timer_ms_raw = ext_i32(raw, 0x100); o.level = ext_i32(raw, 0xfc);
      o.life_override_ms_raw = ext_i32(raw, 0x114);
      /* Live Tornado: tick 818 => 400, tick 825 => 50. This is a
         countdown, NOT the sandbox bridge's assumed elapsed time. Do not
         carry that build's data+0x170 lifetime formula into this build. */
      if (o.timer_ms_raw >= 0) o.remaining_ms = o.timer_ms_raw;
      if (extra.effect_count < MAX_ENTITIES) extra.effects[extra.effect_count++] = o;
    }
  }
}

static void emit_extended_entity(const EntityFrame *e) {
  printf("{\"address\":\"0x%" PRIx64 "\",\"category\":%d,\"kind\":%d,\"side\":%d,"
         "\"x\":%d,\"y\":%d,\"card_id\":%d,\"level\":%d,\"hp\":%d,\"max_hp\":%d,"
         "\"behavior_state_raw\":%d,\"evo\":%d}", e->address, e->category, e->kind, e->side,
         e->x, e->y, e->card_id, e->level, e->hp, e->max_hp, e->behavior, ext_evo(e->card_id));
}
static void emit_optional_pointer(uint64_t p) {
  if (p) printf("\"0x%" PRIx64 "\"", p); else printf("null");
}
static void emit_extra(int active, int coherent) {
  /* The caller's tick/chain bracket covers these reads. Suppress nonunit
     payload on a failed or incoherent frame and expose validity explicitly. */
  int valid = active && coherent && extra.read_errors == 0;
  printf(",\"extension\":{\"build\":160402012,\"valid\":%s,"
         "\"evo_basis\":\"card_id_table_13\",\"unknown_nonunits\":%d,\"read_errors\":%d},"
         "\"projectiles\":[", valid ? "true" : "false", extra.unknown_nonunits, extra.read_errors);
  for (int i = 0; valid && i < extra.projectile_count; ++i) {
    const ExtraObject *o = &extra.projectiles[i];
    printf("%s{\"address\":\"0x%" PRIx64 "\",\"generation_key\":%d,\"vtable_rva\":\"0x%" PRIx64
           "\",\"side\":%d,\"x\":%d,\"y\":%d,\"target_x\":%d,\"target_y\":%d,\"card_id\":%d,\"source\":",
           i ? "," : "", o->address, o->generation_key, o->vtable_rva, o->side, o->x, o->y,
           o->target_x, o->target_y, o->card_id);
    emit_optional_pointer(o->source); printf(",\"target\":"); emit_optional_pointer(o->target);
    printf(",\"attached_owner\":"); emit_optional_pointer(o->attached_owner); putchar('}');
  }
  printf("],\"effects\":[");
  for (int i = 0; valid && i < extra.effect_count; ++i) {
    const ExtraObject *o = &extra.effects[i];
    printf("%s{\"address\":\"0x%" PRIx64 "\",\"generation_key\":%d,\"vtable_rva\":\"0x%" PRIx64
           "\",\"side\":%d,\"x\":%d,\"y\":%d,\"card_id\":%d,\"data_ptr\":\"0x%" PRIx64
           "\",\"level_raw\":%d,\"timer_ms_raw\":%d,\"life_override_ms_raw\":%d,\"remaining_ms\":",
           i ? "," : "", o->address, o->generation_key, o->vtable_rva, o->side, o->x, o->y,
           o->card_id, o->data_ptr, o->level, o->timer_ms_raw, o->life_override_ms_raw);
    if (o->remaining_ms < 0) printf("null"); else printf("%" PRId64, o->remaining_ms);
    putchar('}');
  }
  putchar(']');
}
